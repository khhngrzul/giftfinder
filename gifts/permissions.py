from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Уншихыг хүн бүр, засах/устгахыг зөвхөн эзэн эсвэл админ."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'created_by', None) or getattr(obj, 'user', None)
        return request.user.is_staff or owner == request.user