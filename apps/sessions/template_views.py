from django.shortcuts import render, redirect
from apps.users.template_views import get_user_from_request


def sessions_page(request):
    user = get_user_from_request(request)
    if not user:
        return redirect('auth')
    return render(request, 'sessions/sessions.html', {'user': user})
