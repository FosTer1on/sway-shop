from django.db import migrations


def migrate_outfit_images(apps, schema_editor):
    Outfit = apps.get_model("product", "Outfit")
    OutfitImage = apps.get_model("product", "OutfitImage")

    for outfit in Outfit.objects.exclude(image=""):
        if outfit.image:
            OutfitImage.objects.get_or_create(
                outfit=outfit,
                image=outfit.image,
                defaults={
                    "order": 0,
                },
            )


def reverse_migrate_outfit_images(apps, schema_editor):
    OutfitImage = apps.get_model("product", "OutfitImage")
    OutfitImage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0019_outfitimage"),
    ]

    operations = [
        migrations.RunPython(
            migrate_outfit_images,
            reverse_migrate_outfit_images,
        ),
    ]