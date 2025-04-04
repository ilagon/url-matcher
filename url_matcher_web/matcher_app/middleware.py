"""
Custom middleware for the URL Matcher application.
Provides enhanced CSRF protection while allowing flexibility for dokploy deployment.
"""

from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FlexibleCSRFMiddleware(CsrfViewMiddleware):
    """
    A more flexible CSRF middleware that logs CSRF failures and provides
    better error messages for debugging in production environments.
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Process the view with enhanced logging for CSRF failures.
        """
        # Skip CSRF checks for specific paths if needed
        exempt_paths = getattr(settings, 'CSRF_EXEMPT_PATHS', [])
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
            
        # Check for CSRF exempt decorator
        if getattr(callback, 'csrf_exempt', False):
            return None
            
        # Perform standard CSRF check with enhanced logging
        result = super().process_view(request, callback, callback_args, callback_kwargs)
        
        # Log CSRF failures for debugging
        if result is not None:  # This means CSRF validation failed
            logger.warning(
                f"CSRF verification failed for path: {request.path}, "
                f"Referer: {request.META.get('HTTP_REFERER', 'None')}, "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'None')}"
            )
            
        return result
