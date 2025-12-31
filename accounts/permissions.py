from rest_framework import permissions

class IsCoordinatorOrReadOnly(permissions.BasePermission):
    """
    Allows Coordinators and Admins full access. 
    Viewers and others get Read-Only access.
    """
    def has_permission(self, request, view):
        # Allow any safe method (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user has a profile and the right role
        return request.user.is_authenticated and request.user.userprofile.role in ['ADMIN', 'COORDINATOR']

class IsOwnerOrCoordinator(permissions.BasePermission):
    """
    Custom permission to only allow owners of a log to edit it.
    Coordinators can edit any log.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is a Coordinator/Admin
        if request.user.userprofile.role in ['ADMIN', 'COORDINATOR']:
            return True

        # Fellows can only edit if they are the 'owner' of the record
        # This assumes your model has a field named 'user' or 'fellow'
        return obj.fellow.user == request.user