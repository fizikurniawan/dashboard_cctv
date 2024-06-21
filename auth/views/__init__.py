from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth.models import User
from auth.models import AuthToken
from libs.auth import create_auth_token, create_refresh_token
from typing import Tuple
from ..serializers import SignInSerializer, GetAuthFromRefreshTokenSZ
from user.serializers import UserSerializer


class SignInViewSet(GenericViewSet):
    serializer_class = SignInSerializer

    def _process_login(self, user: User, device_id: str) -> Tuple[str, str]:
        sid = transaction.savepoint()
        try:
            token = create_auth_token(user)
            refresh_token = create_refresh_token(user)

            AuthToken.objects.create(token=token, user=user, device_id=device_id)
        except:
            transaction.savepoint_rollback(sid)
        transaction.savepoint_commit(sid)

        return token, refresh_token

    @transaction.atomic
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        device_id = serializer.validated_data.get("device_id")

        token, refresh_token = self._process_login(user, device_id)

        response_data = {"token": token, "refresh_token": refresh_token}
        return Response(response_data)


class RefreshTokenViewSet(GenericViewSet):
    serializer_class = GetAuthFromRefreshTokenSZ

    def create(self, request):
        sz_class = self.get_serializer(data=request.data)
        sz_class.is_valid(raise_exception=True)

        validated_data = sz_class.validated_data
        user = validated_data["user"]

        token = create_auth_token(user)
        refresh_token = create_refresh_token(user)

        AuthToken.objects.create(token=token, user=user)

        return Response({"token": token, "refresh_token": refresh_token})


class MeViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def list(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
