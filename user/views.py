from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs import constants
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.permission import RBACPermission
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, UserWriteSerializer, RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("full_name", "last_name", "username")
    permission_classes = (IsAuthenticated, RBACPermission)
    queryset = User.objects.filter().order_by("-date_joined")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    PERMISSION_REQUIRES = {
        constants.PRINCIPAL_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
        ],
        constants.SUPERADMIN_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
        ],
    }

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return UserWriteSerializer
        return UserSerializer


class RoleViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    permission_classes = (IsAuthenticated, RBACPermission)
    queryset = Group.objects.filter().order_by("-id")
    serializer_class = RoleSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    PERMISSION_REQUIRES = {
        constants.PRINCIPAL_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
        ],
        constants.SUPERADMIN_ROLE: [
            "list",
            "create",
            "retrieve",
            "partial_update",
            "destroy",
        ],
    }
