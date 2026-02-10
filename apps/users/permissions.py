from rest_framework.permissions import BasePermission


class HasGroupPermission(BasePermission):
    group_name = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.groups.filter(
            name=self.group_name
        ).exists()


class IsAdmin(HasGroupPermission):
    group_name = "admin"


class IsEditor(HasGroupPermission):
    group_name = "editor"


class IsViewer(HasGroupPermission):
    group_name = "viewer"