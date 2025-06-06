from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token['user_id']
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    ASGI middleware for token auth using DRF SimpleJWT with query string.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Parse token from query string
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            try:
                validated_token = AccessToken(token)
                scope['user'] = await get_user(validated_token)
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)


# Wrapper to use in asgi.py
def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
