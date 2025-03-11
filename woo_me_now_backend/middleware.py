import threading

_request_local = threading.local()

class RequestMiddleware:
    """Middleware to store request in thread-local storage."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_local.request = request  # Store request
        response = self.get_response(request)
        return response

    @staticmethod
    def get_request():
        return getattr(_request_local, "request", None)
