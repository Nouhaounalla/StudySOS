from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class CookieJWTAuthentication(JWTAuthentication):
    
    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                return (user, validated_token)
            except Exception:
                pass
        
        header = self.get_header(request)
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        
        return (user, validated_token)