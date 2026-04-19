from django.urls import path
from . import template_views

urlpatterns = [
    path('', template_views.questions_page, name='questions'),
    path('<int:pk>/', template_views.question_detail_page, name='question-detail'),
]
