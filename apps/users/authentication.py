from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # If no token cookie, return None (allows unauthenticated access)
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None  # <-- IMPORTANT: Don't raise exception here
        
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            return None  # Or raise AuthenticationFailed if you want to block