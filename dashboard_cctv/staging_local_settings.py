# Copy this file to local_settings.py and configure it

import os
import datetime

# BASE_URL = "http://127.0.0.1:8000/"
BASE_URL = "https://cctv.arnatech.id/"
FE_BASE_URL = "https://dashboard-cctv.staging.arnatech.id/"
DASHBOARD_BASE_URL = "https://dashboard-cctv-dashboard.staging.arnatech.id/"
DEBUG = True
PRODUCTION = False
SITE_ID = 1
CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "dashboard_cctv_db",
        "USER": "postgres",
        "PASSWORD": "7a8UJbM2GgBWaseh0lnP3O5i1i5nINXk",
        "HOST": "172.105.124.43",
        "PORT": "5432",
        "TEST": {"NAME": "dashboard_cctv_db_staging"},
    },
    "vms_system": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "vms_system",
        "USER": "admin",
        "PASSWORD": "admin123",
        "HOST": "172.16.7.7",
        "PORT": "3306",
        "TEST": {"NAME": "your_db_name"},
    },
}

EMAIL_HOST = "mail.arnatech.id"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "admin@arnatech.id"
EMAIL_HOST_PASSWORD = "hkZ01uVfAqQj95ip"

# email verify token expired. using timedelta
from datetime import timedelta

EXPIRED_VERIFY_TOKEN = timedelta(hours=4)  # set 4 hours after sending email

USE_S3 = True
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
# STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
AWS_ACCESS_KEY_ID = "FQYH52PFVIJ97EH7NX37"
AWS_SECRET_ACCESS_KEY = "NUHTUy3LwmwkWCGOZPGRPB6jo56QDgNfMpldeCIi"
AWS_STORAGE_BUCKET_NAME = "escrow-sg"
AWS_S3_ENDPOINT_URL = "https://%s.ap-south-1.linodeobjects.com" % (
    AWS_STORAGE_BUCKET_NAME
)
AWS_S3_SIGNATURE_VERSION = "s3v4"


# default JWT
JWT_SECRET_KEY = "barakadut"
JWT_ALGORITHMS = ["HS256"]

# JWT for auth token
AUTH_JWT_SECRET_KEY = "barakadut123"
AUTH_JWT_ALGORITHMS = ["HS256"]

# JWT for refresh token
REFRESH_JWT_SECRET_KEY = "barakadut890"
REFRESH_JWT_ALGORITHMS = ["HS256"]

HLS_BASE_URL = "https://stream.arnatech.id"
