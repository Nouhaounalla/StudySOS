from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from .models import Question, Answer, Subject, QuestionReport
from .serializers import (
    QuestionSerializer, QuestionDetailSerializer,
    AnswerSerializer, SubjectSerializer, QuestionReportSerializer
)
from apps.notifications.utils import send_notification


# ---------- Subjects ----------

@api_view(['GET'])
@permission_classes([AllowAny])
def list_subjects(request):
    subjects = Subject.objects.all()
    return Response(SubjectSerializer(subjects, many=True).data)


# ---------- Questions ----------

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def questions_list(request):
    if request.method == 'GET':
        qs = Question.objects.select_related('author', 'subject').all()

        subject = request.query_params.get('subject')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('q')
        ordering = request.query_params.get('ordering', '-created_at')

        if subject:
            qs = qs.filter(subject__slug=subject)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))

        allowed_orderings = ['-created_at', 'created_at', '-views_count']
        if ordering in allowed_orderings:
            qs = qs.order_by(ordering)

        serializer = QuestionSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    # POST - requires auth
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = QuestionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def question_detail(request, pk):
    try:
        question = Question.objects.select_related('author', 'subject').get(pk=pk)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        question.views_count += 1
        question.save(update_fields=['views_count'])
        serializer = QuestionDetailSerializer(question, context={'request': request})
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PATCH':
        if question.author != request.user and request.user.role != 'admin':
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuestionSerializer(question, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if question.author != request.user and request.user.role != 'admin':
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_resolved(request, pk):
    try:
        question = Question.objects.get(pk=pk, author=request.user)
    except Question.DoesNotExist:
        return Response({'error': 'Not found or not your question.'}, status=status.HTTP_404_NOT_FOUND)
    question.status = 'resolved'
    question.save(update_fields=['status'])
    return Response({'status': 'resolved'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_question(request, pk):
    try:
        question = Question.objects.get(pk=pk)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)
    data = {**request.data, 'question': pk}
    serializer = QuestionReportSerializer(data=data)
    if serializer.is_valid():
        serializer.save(reporter=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Answers ----------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_answer(request, question_pk):
    try:
        question = Question.objects.get(pk=question_pk, status='open')
    except Question.DoesNotExist:
        return Response({'error': 'Question not found or closed.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AnswerSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        answer = serializer.save(author=request.user, question=question)
        # Notify question author
        if question.author and question.author != request.user:
            send_notification(
                recipient=question.author,
                notif_type='new_answer',
                message=f'{request.user.get_full_name()} a répondu à votre question "{question.title}"',
                reference_id=question.id
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_answer(request, pk):
    try:
        answer = Answer.objects.select_related('question').get(pk=pk)
    except Answer.DoesNotExist:
        return Response({'error': 'Answer not found.'}, status=status.HTTP_404_NOT_FOUND)

    if answer.question.author != request.user:
        return Response({'error': 'Only the question author can accept an answer.'}, status=status.HTTP_403_FORBIDDEN)

    # Unaccept previous
    answer.question.answers.filter(is_accepted=True).update(is_accepted=False)
    answer.is_accepted = True
    answer.save(update_fields=['is_accepted'])
    answer.question.status = 'resolved'
    answer.question.save(update_fields=['status'])

    send_notification(
        recipient=answer.author,
        notif_type='answer_accepted',
        message=f'Votre réponse a été acceptée pour "{answer.question.title}"',
        reference_id=answer.question.id
    )
    return Response({'accepted': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upvote_answer(request, pk):
    try:
        answer = Answer.objects.get(pk=pk)
    except Answer.DoesNotExist:
        return Response({'error': 'Answer not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user in answer.upvotes.all():
        answer.upvotes.remove(request.user)
        upvoted = False
    else:
        answer.upvotes.add(request.user)
        upvoted = True

    return Response({'upvoted': upvoted, 'upvotes_count': answer.upvotes.count()})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_answer(request, pk):
    try:
        answer = Answer.objects.get(pk=pk)
    except Answer.DoesNotExist:
        return Response({'error': 'Answer not found.'}, status=status.HTTP_404_NOT_FOUND)
    if answer.author != request.user and request.user.role != 'admin':
        return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
    answer.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
