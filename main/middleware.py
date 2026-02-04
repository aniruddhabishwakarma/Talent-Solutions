from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from main.models import User


class JWTAuthenticationMiddleware:
    """
    Middleware to authenticate users via JWT token stored in cookies.
    This allows JWT auth to work seamlessly with Django templates.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to get the access token from cookies
        access_token = request.COOKIES.get(settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'))

        if access_token:
            try:
                # Validate the token
                token = AccessToken(access_token)
                user_id = token.get('user_id')

                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                        request.jwt_authenticated = True
                    except User.DoesNotExist:
                        request.jwt_authenticated = False
            except TokenError:
                # Token is invalid or expired
                request.jwt_authenticated = False
        else:
            request.jwt_authenticated = False

        response = self.get_response(request)
        return response
