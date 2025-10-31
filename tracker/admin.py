from django.contrib import admin
from .models import TrackedProduct, PriceAlert

@admin.register(TrackedProduct)
class TrackedProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'current_price', 'is_in_stock', 'created_at')
    list_filter = ('is_in_stock', 'created_at', 'brand')
    search_fields = ('title', 'brand', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'price_history')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Product Info', {
            'fields': ('user', 'url', 'title', 'brand')
        }),
        ('Pricing', {
            'fields': ('current_price', 'previous_price', 'is_in_stock')
        }),
        ('History', {
            'fields': ('price_history', 'created_at', 'updated_at')
        }),
    )

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'target_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'product__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)