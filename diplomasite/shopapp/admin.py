from django.contrib import admin

from .models import Product, ImagesProduct, Specification, Reviews


class ProductInline(admin.StackedInline):
    model = ImagesProduct


class SpecificationInline(admin.TabularInline):
    model = Specification


class ReviewInline(admin.TabularInline):
    model = Reviews


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'price', 'date', 'count',
                    'freeDelivery', 'rating',)
    list_display_links = "pk", "title"
    ordering = "title", "pk"
    search_fields = "title", "description", "price"
    inlines = [ProductInline, SpecificationInline, ReviewInline]
    fieldsets = [
        (None,
         {
             "fields": ("title", "description"),
         }
         ),
        ("tags",
         {
             "fields": ("tags",)
         }),
        ("category",
         {
             "fields": ("category",)

         }),
        ("count",
         {
             "fields": ("count",)
         }),
        ("price",
         {
             "fields": ("price",)
         }),
        ("rating",
         {
             "fields": ("rating",)

         }),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."
