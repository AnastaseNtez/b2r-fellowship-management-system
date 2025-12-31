from rest_framework import permissions

class IsOwnerOrMentor(permissions.BasePermission):
    """
    Object-level permission to allow owners of an object to edit it.
    Mentors/Coordinators/Staff can edit any log.
    Viewers are restricted to Read-Only via SAFE_METHODS.
    """
    def has_permission(self, request, view):
        # 1. Allow authenticated users to view data (GET, HEAD, OPTIONS)
        # This covers the 'Viewer' role's primary requirement.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # 2. Prevent 'VIEWER' role from any write operations (POST, PUT, DELETE)
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'VIEWER':
            return False

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Safe methods are always allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Mentors/Staff/Superusers can edit/delete anything
        if request.user.is_staff or request.user.is_superuser or hasattr(request.user, 'mentor'):
            return True

        # Fellows can only edit/delete their own training logs
        return obj.fellow.user == request.user