from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg
from .models import Question, Answer, RatingAnswer, RatingTutor, UserSubject
from .serializers import (QuestionSerializer, RatingAnswerSerializer,
                           RatingTutorSerializer, UserSubjectSerializer)
from django.contrib.auth import get_user_model
from django.shortcuts import render
User = get_user_model()


# ── #10 + #13 : Liste questions + filtre statut ──
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def question_list(request):
    status_filter = request.query_params.get('status')
    questions = Question.objects.all().order_by('-created_at')
    if status_filter == 'resolved':
        questions = questions.filter(is_resolved=True)
    elif status_filter == 'unresolved':
        questions = questions.filter(is_resolved=False)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# ── #10 : Marquer une question comme résolue ────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_resolved(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({'error': 'Question introuvable'}, status=404)
    if question.user != request.user:
        return Response({'error': 'Non autorisé'}, status=403)
    question.is_resolved = True
    question.save()
    return Response({'message': 'Question marquée comme résolue'})


# ── #15 : Évaluer une réponse ───────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_answer(request):
    existing = RatingAnswer.objects.filter(
        answer_id=request.data.get('answer'),
        user=request.user
    ).first()
    if existing:
        existing.score = request.data.get('score')
        existing.save()
        return Response({'message': 'Évaluation mise à jour'})
    serializer = RatingAnswerSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ── #21 : Évaluer un tuteur ─────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_tutor(request):
    existing = RatingTutor.objects.filter(
        tutor_id=request.data.get('tutor'),
        student=request.user
    ).first()
    if existing:
        existing.score = request.data.get('score')
        existing.comment = request.data.get('comment', '')
        existing.save()
        return Response({'message': 'Évaluation mise à jour'})
    serializer = RatingTutorSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(student=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutor_average(request, tutor_id):
    result = RatingTutor.objects.filter(tutor_id=tutor_id).aggregate(average=Avg('score'))
    avg = result['average']
    total = RatingTutor.objects.filter(tutor_id=tutor_id).count()
    return Response({
        'average': round(avg, 1) if avg else None,
        'total': total
    })


# ── #18 : Matières de compétence ────────────────
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_subjects(request):
    if request.method == 'GET':
        subjects = UserSubject.objects.filter(user=request.user)
        serializer = UserSubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    if request.method == 'PUT':
        new_subjects = request.data.get('subjects', [])
        UserSubject.objects.filter(user=request.user).delete()
        for s in new_subjects:
            UserSubject.objects.create(user=request.user, subject=s)
        return Response({'message': 'Matières mises à jour'})


# ── Profil (Sprint 1 — garder ces views) ────────
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    if request.method == 'GET':
        from .serializers import UserSerializer
        return Response(UserSerializer(user).data)
    if request.method == 'PUT':
        from .serializers import UserSerializer
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    from .serializers import UserSerializer
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not user.check_password(old_password):
        return Response({'error': 'Ancien mot de passe incorrect'}, status=400)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Mot de passe changé'})


@api_view(['GET'])
def profile_page(request):
    from django.http import HttpResponse
    return HttpResponse("Profile page")

def questions_page(request):
    return render(request, 'questions.html')
def login_page(request):
    return render(request, 'login.html')
def subjects_page(request):
    return render(request, 'subjects.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tutors_list(request):
    tutors = User.objects.filter(role='tuteur')
    from .serializers import UserSerializer
    serializer = UserSerializer(tutors, many=True)
    return Response(serializer.data)

def tutor_rating_page(request):
    return render(request, 'tutor_rating.html')

def question_detail_page(request, question_id):
    return render(request, 'question_detail.html')