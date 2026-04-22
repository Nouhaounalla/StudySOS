from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Session, Review
from .serializers import Tutoringsessionserializer, ReviewSerializer
from apps.notifications.utils import send_notification


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tutoringsessions_list(request):
    if request.method == 'GET':
        role = request.query_params.get('role', 'student')
        if role == 'tutor':
            tutoringsessions = Session.objects.filter(tutor=request.user).select_related('student', 'tutor', 'subject')
        else:
            tutoringsessions = Session.objects.filter(student=request.user).select_related('student', 'tutor', 'subject')

        status_filter = request.query_params.get('status')
        if status_filter:
            tutoringsessions = tutoringsessions.filter(status=status_filter)

        return Response(Tutoringsessionserializer(tutoringsessions, many=True, context={'request': request}).data)

    # POST - book a session
    serializer = Tutoringsessionserializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        session = serializer.save(student=request.user)
        send_notification(
            recipient=session.tutor,
            notif_type='session_request',
            message=f'{request.user.get_full_name()} a demandé une session : "{session.title}"',
            reference_id=session.id
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def session_detail(request, pk):
    try:
        session = Session.objects.select_related('student', 'tutor', 'subject').get(pk=pk)
    except Session.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user not in [session.student, session.tutor] and request.user.role != 'admin':
        return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return Response(Tutoringsessionserializer(session, context={'request': request}).data)

    if request.method == 'PATCH':
        new_status = request.data.get('status')
        allowed = {
            'tuteur': ['confirmed', 'cancelled'],
            'etudiant': ['cancelled'],
            'admin': ['confirmed', 'cancelled', 'completed'],
        }
        if new_status and new_status not in allowed.get(request.user.role, []):
            return Response({'error': 'Not allowed to set this status.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = Tutoringsessionserializer(session, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated = serializer.save()
            # Notify the other party
            other = session.student if request.user == session.tutor else session.tutor
            send_notification(
                recipient=other,
                notif_type='session_update',
                message=f'Votre session "{session.title}" est maintenant : {updated.get_status_display()}',
                reference_id=session.id
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request, pk):
    try:
        session = Session.objects.get(pk=pk, student=request.user, status='completed')
    except Session.DoesNotExist:
        return Response({'error': 'Session not found or not completed.'}, status=status.HTTP_404_NOT_FOUND)

    if hasattr(session, 'review'):
        return Response({'error': 'Review already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

    data = {**request.data, 'session': pk}
    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        review = serializer.save(reviewer=request.user, reviewed=session.tutor, session=session)
        # Update tutor session/student counts
        session.tutor.tutoringsessions_count = Session.objects.filter(tutor=session.tutor, status='completed').count()
        session.tutor.students_count = Session.objects.filter(tutor=session.tutor, status='completed').values('student').distinct().count()
        session.tutor.save(update_fields=['tutoringsessions_count', 'students_count'])
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
