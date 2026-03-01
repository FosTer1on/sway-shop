from django.conf import settings


def build_public_url(path: str):
    if not path:
        return None

    return (
        f"{settings.SUPABASE_URL}"
        f"/storage/v1/object/public/"
        f"{settings.SUPABASE_BUCKET}/"
        f"{path}"
    )