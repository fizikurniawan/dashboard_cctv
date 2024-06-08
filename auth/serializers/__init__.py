from rest_framework import serializers as sz
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from libs.auth import decode_refresh_token


class SignInSerializer(sz.Serializer):
    email = sz.EmailField()
    password = sz.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = sz.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password,
            )
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise sz.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise sz.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class GetAuthFromRefreshTokenSZ(sz.Serializer):
    refresh_token = sz.CharField()

    def validate(self, attrs):
        refresh_token = attrs["refresh_token"]
        data, error = decode_refresh_token(refresh_token)

        if error:
            raise sz.ValidationError({"refresh_token": "invalid token"})

        user = User.objects.filter(email=data.get("email", "")).last()
        if not user:
            raise sz.ValidationError({"refresh_token": "invalid token"})

        attrs["user"] = user
        attrs["decoded_token"] = data

        return attrs
