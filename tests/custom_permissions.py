from rest_framework.permissions import BasePermission


def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_active:
            if is_teacher(request.user) or request.user.is_superuser:
                return True
        return False


class IsAllowLibrary(BasePermission):
    def has_permission(self, request, view):
        return request.user and (is_teacher(request.user) or request.user.is_superuser or request.user.is_active)
