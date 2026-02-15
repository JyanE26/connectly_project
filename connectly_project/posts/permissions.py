from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.permissions import BasePermission


def require_group(group_name):
    """
    Decorator to require user to be in a specific group
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not request.user.groups.filter(name=group_name).exists():
                return JsonResponse(
                    {'error': f'Access denied. {group_name} role required.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_any_group(*group_names):
    """
    Decorator to require user to be in any of the specified groups
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not request.user.groups.filter(name__in=group_names).exists():
                return JsonResponse(
                    {'error': f'Access denied. One of these roles required: {", ".join(group_names)}'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Custom Permission Classes
class IsPostAuthor(BasePermission):
    """
    Allows access only to the author of the post
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsCommentAuthor(BasePermission):
    """
    Allows access only to the author of the comment
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Allows read access to everyone, but write access only to admins
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()


class IsAuthorOrReadOnly(BasePermission):
    """
    Allows read access to everyone, but write access only to the author
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return obj.author == request.user


class IsModeratorOrAdmin(BasePermission):
    """
    Allows access only to moderators or admins
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.groups.filter(name__in=['Moderator', 'Admin']).exists()
