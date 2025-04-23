from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'diameter', 'length', 'quantity', 'import_date')
    search_fields = ('name',)
    list_filter = ('import_date',)
