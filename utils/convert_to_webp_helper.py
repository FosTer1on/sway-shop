from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import os


def convert_image_to_webp(image_file, upload_to, quality=82):
    if not image_file:
        return image_file

    if image_file.name.lower().endswith(".webp"):
        return image_file

    img = Image.open(image_file)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    buffer = BytesIO()

    img.save(
        buffer,
        format="WEBP",
        quality=quality,
        method=6,
    )

    base_name = os.path.splitext(os.path.basename(image_file.name))[0]
    new_name = f"{upload_to}/{base_name}.webp"

    return ContentFile(buffer.getvalue(), name=new_name)