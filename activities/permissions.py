from rest_framework import permissions

class IsOwnerOrMentor(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Mentors (staff) can edit anything.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are GET, HEAD, OPTIONS (Read-only)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner or staff/mentors
        return obj.fellow.user == request.user or request.user.is_staff