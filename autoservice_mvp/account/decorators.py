from django.core.exceptions import PermissionDenied

def service_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_service:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
