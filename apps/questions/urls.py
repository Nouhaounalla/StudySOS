from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.list_subjects, name='api-subjects'),
    path('', views.questions_list, name='api-questions'),
    path('<int:pk>/', views.question_detail, name='api-question-detail'),
    path('<int:pk>/resolve/', views.mark_resolved, name='api-question-resolve'),
    path('<int:pk>/report/', views.report_question, name='api-question-report'),
    path('<int:question_pk>/answers/', views.post_answer, name='api-post-answer'),
    path('answers/<int:pk>/accept/', views.accept_answer, name='api-accept-answer'),
    path('answers/<int:pk>/upvote/', views.upvote_answer, name='api-upvote-answer'),
    path('answers/<int:pk>/', views.delete_answer, name='api-delete-answer'),
]
