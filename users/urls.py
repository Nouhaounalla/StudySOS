from django.urls import path
from . import views

urlpatterns = [
    # Sprint 1 — profil
    path('api/profile-page/', views.profile_page),
    path('api/users/profile/', views.profile),
    path('api/users/me/', views.me),
    path('api/users/change-password/', views.change_password),
    # #10 + #13 — questions
    path('api/questions/', views.question_list),
    path('api/questions/<int:question_id>/resolve/', views.mark_resolved),
    # #15 — évaluer une réponse
    path('api/ratings/answer/', views.rate_answer),
    # #21 — évaluer un tuteur
    path('api/ratings/tutor/', views.rate_tutor),
    path('api/ratings/tutor/<int:tutor_id>/', views.tutor_average),
    # #18 — matières de compétence
    path('api/profile/subjects/', views.user_subjects),
    # Pages HTML
    path('questions-page/', views.questions_page),
    path('login/', views.login_page),
    path('subjects/', views.subjects_page),   # ← ICI
    path('api/users/tutors/', views.tutors_list),
    path('tutor-rating/', views.tutor_rating_page),
    path('question/<int:question_id>/', views.question_detail_page),
]