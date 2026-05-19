from django.conf import settings


def build_public_url(path: str):
    if not path:
        return None

    # DEV → локальные media
    if settings.DEBUG:
        return f"{settings.MEDIA_URL}{path}"

    # PROD → Supabase
    return (
        f"{settings.SUPABASE_URL}"
        f"/storage/v1/object/public/"
        f"{settings.SUPABASE_BUCKET}/"
        f"{path}"
    )