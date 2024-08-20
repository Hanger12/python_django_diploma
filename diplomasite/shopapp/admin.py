from django import forms
from django.contrib import admin

from .models import Product, ImagesProduct, Specification, Reviews, Category


class SpecificationInlineForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    value = forms.CharField(max_length=100)

    class Meta:
        model = Product.specifications.through
        fields = ['name', 'value', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Если редактируем существующий объект
            self.fields['name'].initial = self.instance.specification.name
            self.fields['value'].initial = self.instance.specification.value

    def save(self, commit=True):
        instance = super().save(commit=False)
        specification, created = Specification.objects.get_or_create(
            name=self.cleaned_data['name'],
            defaults={'value': self.cleaned_data['value']}
        )
        instance.specification = specification
        if commit:
            instance.save()
        return instance


class ProductImageInline(admin.StackedInline):
    model = ImagesProduct


class SpecificationInline(admin.TabularInline):
    model = Product.specifications.through
    # form = SpecificationInlineForm


class ProductInline(admin.TabularInline):
    model = Specification.product.through


class ReviewInline(admin.TabularInline):
    model = Reviews


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'price', 'date', 'count',
                    'freeDelivery',)
    list_display_links = "pk", "title"
    ordering = "title", "pk"
    search_fields = "title", "description", "price"
    inlines = [ProductImageInline, ReviewInline, SpecificationInline]
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
    ]

    def get_queryset(self, request):
        return Product.objects.prefetch_related("specifications")

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
    fields = ("name", "value",)
    inlines = [ProductInline, ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'image',)
    search_fields = ('title',)
