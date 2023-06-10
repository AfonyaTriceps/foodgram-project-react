from rest_framework import permissions


class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        del view
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
