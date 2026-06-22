from modeltranslation.translator import register, TranslationOptions
from .models import Product, Category, Outfit

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')



@register(Outfit)
class OutfitTranslationOptions(TranslationOptions):
    fields = ("title", "description")