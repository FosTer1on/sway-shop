from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode
from .mixins import TimeStampedModel


def generate_unique_slug(instance, value, slug_field_name='slug'):
    transliterated = unidecode(value)
    slug = base_slug = slugify(transliterated)
    ModelClass = instance.__class__
    counter = 1
    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(id=instance.id).exists():
        slug = f"{base_slug}-{counter}"
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
    size_type = models.ForeignKey(SizeType, on_delete=models.CASCADE, related_name="sizes")
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('size_type', 'name')
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.size_type.name})"

    class Meta:
        verbose_name = _("Размер")
        verbose_name_plural = _("Размеры")


# ========================
# 🏷 Категории
# ========================
class Category(TimeStampedModel):
    name = models.CharField(_("Название категории"), max_length=255, unique=True)
    slug = models.SlugField(max_length=265, unique=True, blank=True)
    icon = models.ImageField(upload_to="category_icons/", blank=True, null=True)
    size_type = models.ForeignKey(SizeType, on_delete=models.SET_NULL, null=True, blank=True)

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
    slug = models.SlugField(max_length=255,unique=True, blank=True)
    icon = models.ImageField(upload_to="brand_icons/", blank=True, null=True)

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
    slug = models.SlugField(max_length=265,unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")


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

    region = models.CharField(
        max_length=20,
        choices=Region.choices,
        default=Region.CHINA
    )

    name = models.CharField(_("Название"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=265, unique=True, blank=True)

    store = models.ForeignKey("Store", on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField(_("Описание"), max_length=2000, blank=True)

    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(_("Скидка %"), default=0)
    quantity = models.PositiveIntegerField(_("Количество"), default=0)

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
            base = f"{self.name}-{self.store.name}"
            self.slug = generate_unique_slug(self, base)
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} — {self.size.name}: {self.quantity}"

    class Meta:
        verbose_name = _("Размер продукта")
        verbose_name_plural = _("Размеры продукта")


# ========================
# 🖼 Фото
# ========================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = _("Фото продукта")
        verbose_name_plural = _("Фотки продукта")

# & Outfits
class Outfit(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=265, unique=True, blank=True)

    image = models.ImageField(upload_to="outfits/")
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Лук")
        verbose_name_plural = _("Луки")


class OutfitItem(models.Model):
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # порядок (чтобы кепка была сверху, например)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
