from rest_framework.permissions import BasePermission


# ================================== ÏĞÎÂÅĞÊÀ ĞÎËÅÉ ÑÎÒĞÓÄÍÈÊÎÂ ==================================
def has_specific_role(allowed_roles):
    class HasSpecificRolePermission(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            return (user.is_authenticated and
                    user.is_staff and
                    user.staff.role and
                    user.staff.role.role_name in allowed_roles)

    return HasSpecificRolePermission
