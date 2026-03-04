from django.db import models
from django.conf import settings
from apps.product.models import Product
from apps.cart.models import CartItem

class Order(models.Model):
    PAYMENT_METHODS = (
        ("cash", "Наличные"),
        ("click", "Click"),
        ("payme", "Payme"),
        ("uzum", "Uzum"),
    )

    STATUS_CHOICES = (
        ("waiting_payment", "Ожидание оплаты"),
        ("waiting_confirmation", "Ожидание подтверждения"),
        ("delivering", "Доставляется"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="waiting_confirmation")

    service_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    products_total = models.DecimalField(max_digits=12, decimal_places=2)
    service_fee_amount = models.DecimalField(max_digits=12, decimal_places=2)
    final_total = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.user})"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    size = models.CharField(max_length=30, null=True, blank=True)

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=12, decimal_places=2)  # цена за 1 шт
    price_with_discount = models.DecimalField(max_digits=12, decimal_places=2)
    final_price = models.DecimalField(max_digits=12, decimal_places=2)  # price_with_discount * quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    class Meta:
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"