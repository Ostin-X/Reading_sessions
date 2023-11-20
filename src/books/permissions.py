from rest_framework import permissions


class ReadOnlyOrStuffPermission(permissions.BasePermission):
    """
    Custom permission to allow access for:
    - Read-only access for unauthenticated users.
    - Full access for authenticated staff or superusers.
    """

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated:
            if user.is_staff or user.is_superuser:
                return True
        return request.method in permissions.SAFE_METHODS


class OwnOrStuffPermission(permissions.BasePermission):
    """
    Custom permission to allow access if:
    - The request user's ID matches the target user's ID,
    - The user is staff,
    - The user is a superuser.
    """

    def has_permission(self, request, view):
        user = request.user

        return user.id == view.kwargs.get("pk") or user.is_staff or user.is_superuser
