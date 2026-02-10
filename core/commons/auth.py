from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication subclass that skips CSRF validation.
    Useful for API clients like Postman that do not handle CSRF tokens.
    """

    def enforce_csrf(self, request):
        return  # Skip CSRF checks


