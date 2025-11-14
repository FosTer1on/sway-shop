from django.db import models
from django.conf import settings
from apps.product.models import Product, Size


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "size")

    def __str__(self):
        return f"{self.product.name} — {self.size.name} x {self.quantity}"

    # 🔥 Цена всегда актуальная (вариант A)
    @property
    def total_price(self):
        return self.product.final_price * self.quantity

    @property
    def base_price(self):
        return self.product.price
