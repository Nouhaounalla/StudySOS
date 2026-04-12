def jwt_user(request):
    """
    Makes user available in templates even with JWT auth.
    Call this in your views or use as context processor.
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken
    
    auth = JWTAuthentication()
    try:
        user_auth_tuple = auth.authenticate(request)
        if user_auth_tuple:
            user, _ = user_auth_tuple
            return {'jwt_user': user, 'is_authenticated': True}
    except InvalidToken:
        pass
    
    return {'jwt_user': None, 'is_authenticated': False}