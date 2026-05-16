from wear_and_go.settings.prod import SUPABASE_URL, SUPABASE_BUCKET


def build_public_url(path: str):
    if not path:
        return None

    return (
        f"{SUPABASE_URL}"
        f"/storage/v1/object/public/"
        f"{SUPABASE_BUCKET}/"
        f"{path}"
    )