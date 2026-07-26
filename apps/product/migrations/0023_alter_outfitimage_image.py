from django.db import migrations, models


def delete_outfit_images_without_image(apps, schema_editor):
    OutfitImage = apps.get_model("product", "OutfitImage")

    OutfitImage.objects.filter(image__isnull=True).delete()
    OutfitImage.objects.filter(image="").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0022_outfitimage_image"),
    ]

    operations = [
        migrations.RunPython(
            delete_outfit_images_without_image,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="outfitimage",
            name="image",
            field=models.ImageField(
                upload_to="outfits",
                verbose_name="Фото",
            ),
        ),
    ]