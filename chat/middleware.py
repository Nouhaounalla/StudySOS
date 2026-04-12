from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        subprotocols = scope.get('subprotocols', [])
        token = None
        
        if len(subprotocols) >= 2 and subprotocols[0] == 'token':
            token = subprotocols[1]
        
        if not token:
            from urllib.parse import parse_qs
            query_string = scope.get('query_string', b'').decode()
            params = parse_qs(query_string)
            token = params.get('token', [None])[0]

        scope['user'] = AnonymousUser()
        
        if token:
            try:
                UntypedToken(token)
                user_id = UntypedToken(token).payload.get('user_id')
                if user_id:
                    scope['user'] = await get_user(user_id)
            except (InvalidToken, TokenError):
                pass

        return await self.inner(scope, receive, send)