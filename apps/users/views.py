from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.conf import settings
from .models import User
from .serializers import RegisterSerializer, UserProfileSerializer, PublicUserSerializer, ChangePasswordSerializer
from django.db import transaction

def set_auth_cookies(response, user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=jwt_settings.get('AUTH_COOKIE', 'access_token'),
        value=access_token,
        max_age=int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
        samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
    )
    response.set_cookie(
        key=jwt_settings.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
        value=refresh_token,
        max_age=int(jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
        samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
    )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response = Response({'message': 'Account created successfully.', 'user_id': user.id},
                            status=status.HTTP_201_CREATED)
        return set_auth_cookies(response, user)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({'error': 'Account is disabled.'}, status=status.HTTP_403_FORBIDDEN)
    user.is_online = True
    user.save(update_fields=['is_online'])
    response = Response({'message': 'Login successful.', 'role': user.role})
    return set_auth_cookies(response, user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        )
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except TokenError:
        pass
    request.user.is_online = False
    request.user.save(update_fields=['is_online'])
    response = Response({'message': 'Logged out successfully.'})
    response.delete_cookie(settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'))
    response.delete_cookie(settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token'))
    return response


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_photo(request):
    if 'photo' not in request.FILES:
        return Response({'error': 'No photo provided.'}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    user.profile_photo = request.FILES['photo']
    user.save(update_fields=['profile_photo'])
    return Response({'profile_photo': request.build_absolute_uri(user.profile_photo.url)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_cover_photo(request):
    if 'photo' not in request.FILES:
        return Response({'error': 'No photo provided.'}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    user.cover_photo = request.FILES['photo']
    user.save(update_fields=['cover_photo'])
    return Response({'cover_photo': request.build_absolute_uri(user.cover_photo.url)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Incorrect current password.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        response = Response({'message': 'Password updated successfully.'})
        return set_auth_cookies(response, user)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    
    # Create response FIRST while user still exists in context
    response = Response({'message': 'Account deleted.'})
    
    # Delete cookies using your JWT auth cookie names
    access_cookie = getattr(settings, 'SIMPLE_JWT', {}).get('AUTH_COOKIE', 'access_token')
    refresh_cookie = getattr(settings, 'SIMPLE_JWT', {}).get('AUTH_COOKIE_REFRESH', 'refresh_token')
    
    response.delete_cookie(access_cookie)
    response.delete_cookie(refresh_cookie)
    
    # Delete user LAST (after response is fully prepared)
    # Use transaction in case related objects block deletion
    try:
        with transaction.atomic():
            user.delete()
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Account deletion failed: {str(e)}")
        return Response(
            {'error': f'Deletion failed: {str(e)}'}, 
            status=500
        )
    
    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def list_tutors(request):
    tutors = User.objects.filter(role='tuteur', is_active=True)
    subject = request.query_params.get('subject')
    search = request.query_params.get('q')
    if subject:
        tutors = [t for t in tutors if subject in (t.subjects or [])]
    if search:
        tutors = tutors.filter(
            username__icontains=search
        ) | tutors.filter(first_name__icontains=search)
    serializer = PublicUserSerializer(tutors, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_profile(request, username):
    try:
        user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = PublicUserSerializer(user, context={'request': request})
    return Response(serializer.data)
