"""dashboard_cctv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from common.router import router as common_router
from cctv.router import router as cctv_router
from vehicle.router import router as vehicle_router
from resident.router import router as resident_router
from user.router import router as user_router
from auth.router import router as auth_router
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Dashboard CCTV API",
        default_version="v1",
        description="API documentation for CCTV Monitoring System",
        terms_of_service="https://www.example.com/policies/terms/",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=settings.BASE_URL,
)

urlpatterns = [
    path("api/auth/", include(auth_router.urls)),
    path("api/common/", include(common_router.urls)),
    path("api/cctv/", include(cctv_router.urls)),
    path("api/vehicle/", include(vehicle_router.urls)),
    path("api/resident/", include(resident_router.urls)),
    path("api/user/", include(user_router.urls)),
    path("i18n/setlang/", set_language, name="set_language"),
    path("i18n/setlang/", set_language, name="set_language"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)