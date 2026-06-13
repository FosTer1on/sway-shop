import os
import dj_database_url

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]


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

AWS_S3_SIGNATURE_VERSION = "s3v4"

AWS_LOCATION = ""

AWS_S3_CUSTOM_DOMAIN = None

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")


SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)

# ==========================
# SECURITY
# ==========================

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Для первого деплоя лучше оставить 0.
# Потом, когда HTTPS точно работает, можно поставить 31536000.
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", 0))

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True