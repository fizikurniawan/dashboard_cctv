from rest_framework import permissions


class RBACPermission(permissions.BasePermission):
    """Usage permission. add PERMISSION_REQUIRES in viewset

    format:
    PERMISSION_REQUIRES = {
        "<role_name>": ["view.action1", "view.action2"],
        "<another_role_name>": ["view.action1", "view.action2"]
    }

    example:

    PERMISSION_REQUIRES = {
        KAUNIT_ROLE: [
            "list",
            "create",
            "retrieve",
        ],
        MANTRI_ROLE: [
            "list",
            "retrieve",
        ],
        USER_REGIONAL_ROLE: ["list"],
        USER_PUSAT_ROLE: ["list"],
    }
    """

    def has_permission(self, request, view):
        PERMISSION_REQUIRES = getattr(view, "PERMISSION_REQUIRES", None)

        group = request.user.groups.first()
        if not group:
            return False

        # get based on group
        permission_by_group = PERMISSION_REQUIRES.get(group.name, [])
        if not permission_by_group:
            return False

        # is action in permission role
        return view.action in permission_by_group
