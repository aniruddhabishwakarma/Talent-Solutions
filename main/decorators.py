from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def jwt_required(view_func):
    """
    Decorator to require JWT authentication.
    Redirects to login page if not authenticated.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """
    Decorator to require admin role.
    Redirects to admin login if not authenticated or not admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('admin_login')

        if not request.user.is_admin():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('admin_login')

        return view_func(request, *args, **kwargs)
    return wrapper


def user_required(view_func):
    """
    Decorator to require user role (non-admin).
    Redirects to user login if not authenticated.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('user_login')

        if request.user.is_admin():
            messages.error(request, 'Please use the admin dashboard.')
            return redirect('admin_dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper


def guest_only(redirect_to='home'):
    """
    Decorator to allow only non-authenticated users.
    Redirects authenticated users to specified page.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_admin():
                    return redirect('admin_dashboard')
                return redirect(redirect_to)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
