import os
import dj_database_url

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    ""
).split(",")

CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    ""
).split(",")


# ==========================
# DATABASE
# ==========================

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL")
    )
}


# ==========================
# WhiteNoise
# ==========================

MIDDLEWARE.insert(
    1,
    'whitenoise.middleware.WhiteNoiseMiddleware'
)

STORAGES = {
    "default": {
        "BACKEND": "utils.supabase_storage.SupabaseMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ==========================
# SUPABASE
# ==========================

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")

AWS_SECRET_ACCESS_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY"
)

AWS_STORAGE_BUCKET_NAME = os.getenv(
    "AWS_STORAGE_BUCKET_NAME"
)

AWS_S3_ENDPOINT_URL = os.getenv(
    "AWS_S3_ENDPOINT_URL"
)

AWS_S3_REGION_NAME = os.getenv(
    "AWS_S3_REGION_NAME"
)

AWS_S3_ADDRESSING_STYLE = "path"

AWS_QUERYSTRING_AUTH = False

AWS_DEFAULT_ACL = None

AWS_S3_FILE_OVERWRITE = False

AWS_S3_VERIFY = True

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")


SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)