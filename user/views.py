from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, UserWriteSerializer, RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("full_name", "last_name", "username")
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = User.objects.filter()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return UserWriteSerializer
        return UserSerializer


class RoleViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = Group.objects.filter()
    serializer_class = RoleSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
