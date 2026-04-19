from django.shortcuts import render, get_object_or_404
from apps.users.template_views import get_user_from_request
from .models import Question, Subject


def questions_page(request):
    user = get_user_from_request(request)
    subjects = Subject.objects.all()
    return render(request, 'questions/questions.html', {'user': user, 'subjects': subjects})


def question_detail_page(request, pk):
    user = get_user_from_request(request)
    question = get_object_or_404(Question, pk=pk)
    subjects = Subject.objects.all()
    return render(request, 'questions/question_detail.html', {
        'user': user,
        'question': question,
        'subjects': subjects,
    })
