from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from singletons.logger_singleton import LoggerSingleton
import time


class APILoggingMiddleware(MiddlewareMixin):
    """Middleware to log all API requests and responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger_singleton = LoggerSingleton()
        self.logger = self.logger_singleton.get_logger()

    def __call__(self, request):
        # Skip logging for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            response = self.get_response(request)
            return response

        # Log request
        start_time = None
        if hasattr(request, 'start_time'):
            start_time = request.start_time
        else:
            start_time = time.time()
            request.start_time = start_time

        # Process the request
        response = self.get_response(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log the API request
        self.logger_singleton.log_api_request(
            method=request.method,
            endpoint=request.path,
            user=request.user if request.user.is_authenticated else None,
            status_code=response.status_code
        )

        # Log performance metrics for slow requests
        if response_time > 1.0:  # Log requests taking more than 1 second
            self.logger_singleton.log_performance_metric(
                metric_name="SLOW_REQUEST",
                value=response_time,
                details=f"Slow request to {request.path}"
            )

        # Log security events for error responses
        if response.status_code >= 400:
            if response.status_code == 401:
                self.logger_singleton.log_security_event(
                    event_type="UNAUTHORIZED_ACCESS",
                    details=f"Unauthorized access attempt to {request.path}",
                    user=request.user if request.user.is_authenticated else None
                )
            elif response.status_code == 403:
                self.logger_singleton.log_security_event(
                    event_type="FORBIDDEN_ACCESS",
                    details=f"Forbidden access attempt to {request.path}",
                    user=request.user if request.user.is_authenticated else None
                )
            elif response.status_code >= 500:
                self.logger_singleton.log_security_event(
                    event_type="SERVER_ERROR",
                    details=f"Server error processing {request.path}",
                    user=request.user if request.user.is_authenticated else None
                )

        return response
