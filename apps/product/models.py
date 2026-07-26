from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode
from .mixins import TimeStampedModel
from utils.convert_to_webp_helper import convert_image_to_webp


def generate_unique_slug(instance, value, slug_field_name="slug", max_length=265):
    transliterated = unidecode(str(value or "item"))
    base_slug = slugify(transliterated)[:max_length].strip("-")

    if not base_slug:
        base_slug = "item"

    ModelClass = instance.__class__
    slug = base_slug
    counter = 1

    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[:max_length - len(suffix)]}{suffix}"
        counter += 1

    return slug


# ========================
# 📏 Типы размеров
# ========================
class SizeType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Название размера")
        verbose_name_plural = _("Название размеров")


# ========================
# 📏 Размеры
# ========================
class Size(models.Model):
    size_type = models.ForeignKey(
        SizeType, on_delete=models.CASCADE, related_name="sizes")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.size_type.name})"

    class Meta:
        unique_together = ('size_type', 'name')
        ordering = ['id']
        verbose_name = _("Размер")
        verbose_name_plural = _("Размеры")


# ========================
# 🏷 Категории
# ========================
class Category(TimeStampedModel):
    name = models.CharField(_("Название категории"),
                            max_length=255, unique=True)
    slug = models.SlugField(max_length=265, unique=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon = models.ImageField(
        upload_to="category_icons/", blank=True, null=True)
    size_type = models.ForeignKey(
        SizeType, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")


# ========================
# 🏷 Бренды и магазины
# ========================
class Brand(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    icon = models.ImageField(upload_to="brand_icons/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Бренд")
        verbose_name_plural = _("Бренды")


class Store(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=265, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")


class SizeChart(models.Model):
    name = models.CharField(_("Название шаблона"), max_length=255, unique=True)

    title = models.CharField(
        _("Заголовок"),
        max_length=255,
        default="Таблица размеров"
    )

    note = models.TextField(
        _("Примечание"),
        blank=True,
        null=True
    )

    columns = models.JSONField(
        _("Колонки"),
        default=list
    )

    rows = models.JSONField(
        _("Строки"),
        default=list
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Таблица размеров")
        verbose_name_plural = _("Таблицы размеров")
        ordering = ["-id"]


class ProductVariantGroup(TimeStampedModel):
    name = models.CharField(_("Название цветовой группы"),
                            max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Цветовой вариант товара")
        verbose_name_plural = _("Цветовые варианты товаров")
        ordering = ["-id"]


# ========================
# 🛍️ Товары
# ========================
class Product(TimeStampedModel):
    class Status(models.TextChoices):
        POPULAR = "popular", _("Популярное")
        BEST_SELLER = "best_seller", _("Бестселлер")

    class Region(models.TextChoices):
        CHINA = "china", "Китай"
        USA = "usa", "США"
        EUROPE = "europe", "Европа"
        RUSSIA = "russia", "Россия"
        UZBEKISTAN = "uzbekistan", "Узбекистан"

    class Gender(models.TextChoices):
        MALE = "male", _("Мужской")
        FEMALE = "female", _("Женский")
        UNISEX = "unisex", _("Унисекс")

    name = models.CharField(_("Название"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=265, unique=True, blank=True)

    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, related_name="products", blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(
        "Brand", on_delete=models.SET_NULL, null=True, blank=True)

    size_chart = models.ForeignKey(
        "SizeChart",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Таблица размеров")
    )

    variant_group = models.ForeignKey(
        "ProductVariantGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Группа цветовых вариантов")
    )

    color_name = models.CharField(
        _("Название цвета"),
        max_length=100,
        blank=True,
        null=True
    )

    color_hex = models.CharField(
        _("HEX код цвета"),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Например: #000000")
    )

    gender = models.CharField(
        _("Пол"),
        max_length=10,
        choices=Gender.choices,
        default=Gender.UNISEX
    )
    region = models.CharField(
        max_length=20,
        choices=Region.choices,
        default=Region.CHINA
    )

    description = models.TextField(_("Описание"), max_length=2000, blank=True)

    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(_("Скидка %"), default=0)
    quantity = models.PositiveIntegerField(_("Количество"), default=0)

    product_link = models.CharField(
        _("Ссылка на товар"), blank=True, null=True)

    cargo = models.DecimalField(
        _("Карго"),
        max_digits=10,
        decimal_places=2,
        default=0
    )

    markup = models.DecimalField(
        _("Наценка"),
        max_digits=10,
        decimal_places=2,
        default=0
    )

    weight = models.DecimalField(
        _("Вес"),
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text=_("Вес в кг")
    )

    delivery_time = models.CharField(
        _("Время доставки"),
        max_length=100,
        default="10-15 дней"
    )

    # 🔹 Новые поля
    is_active = models.BooleanField(_("Активен"), default=True)
    is_season = models.BooleanField(_("Сезонный товар"), default=False)

    # 🔹 Статус: может быть пустым
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=Status.choices,
        blank=True,
        null=True,
        help_text=_("Популярное или Бестселлер (может быть пустым)"),
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            parts = [
                self.name,
                self.brand.name if self.brand else None,
                self.region,
            ]

            base = "-".join(str(part) for part in parts if part)
            self.slug = generate_unique_slug(self, base, max_length=265)

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.price - (self.price * self.discount / 100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-is_season", "-created_at"]
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")


# ========================
# 📦 Количество по размеру
# ========================
class ProductSize(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sizes")
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} — {self.size.name}: {self.quantity}"

    class Meta:
        unique_together = ('product', 'size')
        verbose_name = _("Размер продукта")
        verbose_name_plural = _("Размеры продукта")


# ========================
# 🖼 Фото
# ========================
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.image.name.lower().endswith(".webp"):
            self.image = convert_image_to_webp(
                self.image,
                upload_to="products",
                quality=82
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = _("Фото продукта")
        verbose_name_plural = _("Фотки продукта")


# & Outfits
class Outfit(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", _("Мужской")
        FEMALE = "female", _("Женский")
        UNISEX = "unisex", _("Унисекс")

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=265, unique=True, blank=True)

    image = models.ImageField(upload_to="outfits/")
    description = models.TextField(blank=True)

    gender = models.CharField(
        _("Пол"),
        max_length=10,
        choices=Gender.choices,
        default=Gender.UNISEX
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.PositiveIntegerField(default=0)
    cargo = models.DecimalField(
        _("Карго"),
        max_digits=10,
        decimal_places=2,
        default=0000
    )

    markup = models.DecimalField(
        _("Наценка"),
        max_digits=10,
        decimal_places=2,
        default=0000
    )

    weight = models.DecimalField(
        _("Вес"),
        max_digits=6,
        decimal_places=2,
        default=0.,
        help_text=_("Вес в кг")
    )

    delivery_time = models.CharField(
        _("Время доставки"),
        max_length=100,
        default="1"
    )

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            parts = [
                self.title,
                self.gender,
            ]

            base = "-".join(str(part) for part in parts if part)
            self.slug = generate_unique_slug(self, base, max_length=265)

        if self.image and not self.image.name.lower().endswith(".webp"):
            self.image = convert_image_to_webp(
                self.image,
                upload_to="outfits",
                quality=82
            )

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.price - (self.price * self.discount / 100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Лук")
        verbose_name_plural = _("Луки")


class OutfitImage(models.Model):
    outfit = models.ForeignKey(
        Outfit,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Образ"),
    )

    image = models.ImageField(
        _("Фото"),
        upload_to="outfits",
    )

    order = models.PositiveIntegerField(
        _("Порядок"),
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.image.name.lower().endswith(".webp"):
            self.image = convert_image_to_webp(
                self.image,
                upload_to="outfits",
                quality=82,
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Фото образа: {self.outfit.title}"

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Фото образа")
        verbose_name_plural = _("Фотографии образа")


class OutfitItem(models.Model):
    outfit = models.ForeignKey(
        Outfit, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # порядок (чтобы кепка была сверху, например)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class UserEvent(models.Model):
    class EventType(models.TextChoices):
        PRODUCT_VIEW = "product_view", "Просмотр товара"
        SEARCH = "search", "Поиск"
        FAVORITE_ADD = "favorite_add", "Добавил в избранное"
        FAVORITE_REMOVE = "favorite_remove", "Удалил из избранного"
        CART_ADD = "cart_add", "Добавил в корзину"
        CART_REMOVE = "cart_remove", "Удалил из корзины"
        TELEGRAM_ORDER_CLICK = "telegram_order_click", "Клик Telegram-заказ"

    user = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    event_type = models.CharField(max_length=50, choices=EventType.choices)

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    product_slug = models.SlugField(max_length=265, blank=True, null=True)
    search_query = models.CharField(max_length=255, blank=True, null=True)

    page_url = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)

    metadata = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Событие пользователя"
        verbose_name_plural = "События пользователей"

    def __str__(self):
        return f"{self.event_type} | {self.product_slug or self.search_query or self.user}"
