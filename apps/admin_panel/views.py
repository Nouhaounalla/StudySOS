from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.users.template_views import get_user_from_request
from apps.users.models import User
from apps.questions.models import Question, Answer, QuestionReport, Subject
from apps.tutoringsessions.models import Review
from apps.tutoringsessions.serializers import Tutoringsessionserializer
from apps.notifications.models import Notification


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        if not user or user.role != 'admin':
            return redirect('auth')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard(request):
    user = get_user_from_request(request)
    now = timezone.now()
    last_30 = now - timedelta(days=30)

    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_students': User.objects.filter(role='etudiant', is_active=True).count(),
        'total_tutors': User.objects.filter(role='tuteur', is_active=True).count(),
        'new_users_month': User.objects.filter(date_joined__gte=last_30).count(),
        'total_questions': Question.objects.count(),
        'open_questions': Question.objects.filter(status='open').count(),
        'resolved_questions': Question.objects.filter(status='resolved').count(),
        'total_tutoringsessions': Session.objects.count(),
        'pending_tutoringsessions': Session.objects.filter(status='pending').count(),
        'completed_tutoringsessions': Session.objects.filter(status='completed').count(),
        'pending_reports': QuestionReport.objects.filter(is_resolved=False).count(),
        'online_users': User.objects.filter(is_online=True).count(),
    }

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_questions = Question.objects.select_related('author', 'subject').order_by('-created_at')[:5]
    pending_reports = QuestionReport.objects.filter(is_resolved=False).select_related('question', 'reporter')[:5]

    return render(request, 'admin/dashboard.html', {
        'user': user,
        'stats': stats,
        'recent_users': recent_users,
        'recent_questions': recent_questions,
        'pending_reports': pending_reports,
    })


@admin_required
def manage_users(request):
    user = get_user_from_request(request)
    users = User.objects.all().order_by('-date_joined')

    role_filter = request.GET.get('role')
    search = request.GET.get('q')
    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))

    return render(request, 'admin/users.html', {
        'user': user,
        'users': users,
        'role_filter': role_filter,
        'search': search,
    })


@admin_required
def toggle_user_active(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    target = get_object_or_404(User, pk=pk)
    if target.role == 'admin':
        return JsonResponse({'error': 'Cannot deactivate admin'}, status=403)
    target.is_active = not target.is_active
    target.save(update_fields=['is_active'])
    return JsonResponse({'is_active': target.is_active})


@admin_required
def delete_user(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    target = get_object_or_404(User, pk=pk)
    if target.role == 'admin':
        return JsonResponse({'error': 'Cannot delete admin'}, status=403)
    target.delete()
    return JsonResponse({'deleted': True})


@admin_required
def manage_questions(request):
    user = get_user_from_request(request)
    questions = Question.objects.select_related('author', 'subject').annotate(
        answers_count=Count('answers')
    ).order_by('-created_at')

    status_filter = request.GET.get('status')
    subject_filter = request.GET.get('subject')
    search = request.GET.get('q')

    if status_filter:
        questions = questions.filter(status=status_filter)
    if subject_filter:
        questions = questions.filter(subject__slug=subject_filter)
    if search:
        questions = questions.filter(Q(title__icontains=search) | Q(content__icontains=search))

    subjects = Subject.objects.all()
    return render(request, 'admin/questions.html', {
        'user': user,
        'questions': questions,
        'subjects': subjects,
        'status_filter': status_filter,
    })


@admin_required
def delete_question(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return JsonResponse({'deleted': True})


@admin_required
def manage_reports(request):
    user = get_user_from_request(request)
    reports = QuestionReport.objects.select_related(
        'question', 'reporter'
    ).order_by('is_resolved', '-created_at')
    return render(request, 'admin/reports.html', {
        'user': user,
        'reports': reports,
    })


@admin_required
def resolve_report(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    report = get_object_or_404(QuestionReport, pk=pk)
    report.is_resolved = True
    report.save(update_fields=['is_resolved'])
    return JsonResponse({'resolved': True})


@admin_required
def manage_tutoringsessions(request):
    user = get_user_from_request(request)
    tutoringsessions = Session.objects.select_related('student', 'tutor', 'subject').order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        tutoringsessions = tutoringsessions.filter(status=status_filter)

    return render(request, 'admin/tutoringsessions.html', {
        'user': user,
        'tutoringsessions': tutoringsessions,
        'status_filter': status_filter,
    })


@admin_required
def statistics(request):
    user = get_user_from_request(request)
    now = timezone.now()

    # Users over last 7 days
    user_registrations = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        count = User.objects.filter(
            date_joined__date=day.date()
        ).count()
        user_registrations.append({'date': day.strftime('%d/%m'), 'count': count})

    # Questions per subject
    questions_by_subject = list(
        Subject.objects.annotate(q_count=Count('questions')).values('name', 'q_count').order_by('-q_count')[:8]
    )

    # Session statuses
    session_stats = {
        'pending': Session.objects.filter(status='pending').count(),
        'confirmed': Session.objects.filter(status='confirmed').count(),
        'completed': Session.objects.filter(status='completed').count(),
        'cancelled': Session.objects.filter(status='cancelled').count(),
    }

    return render(request, 'admin/statistics.html', {
        'user': user,
        'user_registrations': user_registrations,
        'questions_by_subject': questions_by_subject,
        'session_stats': session_stats,
    })
