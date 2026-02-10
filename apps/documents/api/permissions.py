from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.users.permissions import IsAdmin, IsEditor, IsViewer


class DocumentRBACPermission(BasePermission):
    """
    Enforce RBAC for document operations:
    - admin: full access
    - editor: create/update but cannot delete
    - viewer: read-only
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin has full access
        if IsAdmin().has_permission(request, view):
            return True

        # View-only methods
        if request.method in SAFE_METHODS:
            return IsViewer().has_permission(request, view) or IsEditor().has_permission(
                request, view
            )

        # Mutating methods (non-safe)
        if request.method in ("POST", "PUT", "PATCH"):
            return IsEditor().has_permission(request, view)

        if request.method == "DELETE":
            # only admin (handled above) can delete; editors/viewers cannot
            return False

        return False


