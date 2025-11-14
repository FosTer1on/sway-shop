from django.db import models
from django.conf import settings
from apps.product.models import Product


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # один товар один раз
        ordering = ["-created_at"]


    def __str__(self):
        return f"{self.user} → {self.product}"
