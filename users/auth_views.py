# users/auth_views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.middleware import csrf
from rest_framework_simplejwt.exceptions import TokenError
import traceback

# Import the custom serializer
from .serializers import EmailTokenObtainSerializer


def set_jwt_cookies(response, access_token, refresh_token):
    """Helper function to set JWT cookies with secure settings"""
    
    # Access token cookie (short-lived, HttpOnly)
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAME_SITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    
    # Refresh token cookie (longer-lived, HttpOnly)
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        value=refresh_token,
        expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAME_SITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    
    return response


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            print(f"Login attempt with data: {request.data}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                access_token = response.data.get('access')
                refresh_token = response.data.get('refresh')
                
                from .models import User
                email = request.data.get('email') or request.data.get('username')
                try:
                    if '@' in str(email):
                        user = User.objects.get(email=email)
                    else:
                        user = User.objects.get(username=email)
                except User.DoesNotExist:
                    user = None
                
                # Check if profile is complete
                profile_complete = (
                    user and 
                    user.first_name and 
                    user.last_name and 
                    user.role
                )
                
                # Determine redirect URL
                redirect_url = '/api/users/profile-page/' if profile_complete else '/api/users/profile_info/'
                
                new_response = Response({
                    'status': 'success',
                    'message': 'Login successful',
                    'redirect_url': redirect_url,
                    'user': {
                        'id': user.id if user else None,
                        'email': user.email if user else '',
                        'username': user.username if user else '',
                        'role': getattr(user, 'role', 'etudiant') if user else 'etudiant',
                        'first_name': getattr(user, 'first_name', '') if user else '',
                        'last_name': getattr(user, 'last_name', '') if user else '',
                        'profile_complete': profile_complete
                    }
                }, status=status.HTTP_200_OK)
                
                set_jwt_cookies(new_response, access_token, refresh_token)
                new_response['X-CSRFToken'] = csrf.get_token(request)
                
                print(f"Login successful for user: {user.username if user else 'unknown'}, profile_complete: {profile_complete}")
                return new_response
            
            return response
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response(
                {'status': 'error', 'message': 'Email ou mot de passe incorrect'},
                status=status.HTTP_401_UNAUTHORIZED
            )
class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom refresh view that reads refresh token from cookie
    and sets new access token as cookie.
    """
    
    def post(self, request, *args, **kwargs):
        try:
            # Get refresh token from cookie instead of request body
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            
            if not refresh_token:
                return Response(
                    {'status': 'error', 'message': 'Refresh token not found in cookies'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            try:
                # Validate and create new tokens
                refresh = RefreshToken(refresh_token)
                access_token = str(refresh.access_token)
                
                # If rotation is enabled, get new refresh token too
                new_refresh_token = str(refresh) if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False) else refresh_token
                
                # Blacklist old token if rotation is enabled
                if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION', False):
                    refresh.blacklist()
                
                # Create response
                response = Response({
                    'status': 'success',
                    'message': 'Token refreshed successfully'
                }, status=status.HTTP_200_OK)
                
                # Set new cookies
                set_jwt_cookies(response, access_token, new_refresh_token)
                
                return response
                
            except TokenError as e:
                return Response(
                    {'status': 'error', 'message': f'Invalid refresh token: {str(e)}'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            print(f"Refresh error: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'status': 'error', 'message': 'Erreur lors du rafraîchissement du token'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    Logout view that blacklists refresh token and clears cookies.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get refresh token from cookie
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            
            if refresh_token:
                try:
                    # Blacklist the refresh token
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except TokenError:
                    pass  # Token already invalid
            
            # Create response
            response = Response({
                'status': 'success',
                'message': 'Successfully logged out'
            }, status=status.HTTP_205_RESET_CONTENT)
            
            # Clear cookies by setting them to expire immediately
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            
            return response
            
        except Exception as e:
            print(f"Logout error: {str(e)}")
            print(traceback.format_exc())
            # Even if error, clear cookies
            response = Response({
                'status': 'success',
                'message': 'Logged out'
            }, status=status.HTTP_205_RESET_CONTENT)
            
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            
            return response


class LogoutAllDevicesView(APIView):
    """
    Logout from all devices by blacklisting ALL outstanding refresh tokens.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
            
            # Blacklist all refresh tokens for this user
            tokens = OutstandingToken.objects.filter(user=request.user)
            blacklisted_count = 0
            
            for token in tokens:
                _, created = BlacklistedToken.objects.get_or_create(token=token)
                if created:
                    blacklisted_count += 1
            
            response = Response({
                'status': 'success',
                'message': f'Logged out from all devices. Blacklisted {blacklisted_count} tokens.'
            }, status=status.HTTP_205_RESET_CONTENT)
            
            # Clear current cookies too
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            
            return response
            
        except Exception as e:
            print(f"Logout all error: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'status': 'error', 'message': 'Erreur lors de la déconnexion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )