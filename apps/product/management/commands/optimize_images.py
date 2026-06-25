from io import BytesIO
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from PIL import Image

from apps.product.models import ProductImage, Outfit


def optimize_image_field(instance, field_name, upload_to, quality=82, delete_old=False):
    image_field = getattr(instance, field_name)

    if not image_field:
        return "skipped", "no image"

    if image_field.name.lower().endswith(".webp"):
        return "skipped", "already webp"

    old_name = image_field.name

    try:
        image_field.open("rb")
        img = Image.open(image_field)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=quality, method=6)

        base_name = os.path.splitext(os.path.basename(old_name))[0]
        new_name = f"{upload_to}/{base_name}.webp"

        image_field.save(
            new_name,
            ContentFile(buffer.getvalue()),
            save=False
        )

        instance.save(update_fields=[field_name])

        if delete_old and default_storage.exists(old_name):
            default_storage.delete(old_name)

        return "converted", old_name

    except Exception as e:
        return "error", str(e)


class Command(BaseCommand):
    help = "Convert product and outfit images to WebP"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--delete-old", action="store_true")
        parser.add_argument("--quality", type=int, default=82)

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        delete_old = options["delete_old"]
        quality = options["quality"]

        targets = []

        for item in ProductImage.objects.exclude(image=""):
            targets.append((item, "image", "products",
                           f"ProductImage #{item.id}"))

        for item in Outfit.objects.exclude(image=""):
            targets.append((item, "image", "outfits", f"Outfit #{item.id}"))

        converted = 0
        skipped = 0
        errors = 0

        self.stdout.write(f"Found images: {len(targets)}")
        self.stdout.write(f"Quality: {quality}")
        self.stdout.write(f"Delete old: {delete_old}")
        self.stdout.write(f"Dry run: {dry_run}")

        for instance, field_name, upload_to, label in targets:
            image_field = getattr(instance, field_name)

            if not image_field or image_field.name.lower().endswith(".webp"):
                skipped += 1
                continue

            if dry_run:
                converted += 1
                self.stdout.write(f"[DRY] {label}: {image_field.name}")
                continue

            status, message = optimize_image_field(
                instance=instance,
                field_name=field_name,
                upload_to=upload_to,
                quality=quality,
                delete_old=delete_old,
            )

            if status == "converted":
                converted += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Converted {label}: {message}"))
            elif status == "skipped":
                skipped += 1
            else:
                errors += 1
                self.stdout.write(self.style.ERROR(
                    f"Error {label}: {message}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Converted: {converted}, skipped: {skipped}, errors: {errors}"
            )
        )
