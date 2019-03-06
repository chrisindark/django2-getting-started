from rest_framework import permissions


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view, obj=None):
        if request.user and request.user.is_authenticated:
            return False
        return True
