from django.shortcuts import render, redirect
from apps.users.authentication import CookieJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


def get_user_from_request(request):
    auth = CookieJWTAuthentication()
    try:
        result = auth.authenticate(request)
        if result:
            return result[0]
    except (InvalidToken, Exception):
        pass
    return None


def home(request):
    user = get_user_from_request(request)
    if user:
        return redirect('profile')
    return redirect('auth')


def auth_page(request):
    user = get_user_from_request(request)
    if user:
        return redirect('profile')
    return render(request, 'auth/auth.html')


def profile_info(request):
    user = get_user_from_request(request)
    if not user:
        return redirect('auth')
    return render(request, 'profile/profile_info.html', {'user': user})


def profile_page(request):
    user = get_user_from_request(request)
    if not user:
        return redirect('auth')
    return render(request, 'profile/profile.html', {'user': user})


def public_profile_page(request, username):
    from .models import User
    try:
        profile_user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404
    user = get_user_from_request(request)
    return render(request, 'profile/public_profile.html', {
        'user': user,
        'profile_user': profile_user,
    })


def tutors_page(request):
    user = get_user_from_request(request)
    return render(request, 'profile/tutors.html', {'user': user})
