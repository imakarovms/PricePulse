from rest_framework import serializers
from .models import TrackedProduct, PriceAlert

class TrackedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedProduct
        fields = [
            'id', 'url', 'title', 'brand', 'current_price', 
            'previous_price', 'is_in_stock', 'created_at', 
            'updated_at', 'price_history'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'price_history']
    
    def validate_url(self, value):
        """Validate that URL is from supported stores"""
        supported_stores = [
            'ozon.ru', 'wildberries.ru', 'dns-shop.ru', 
            'citilink.ru', 'mvideo.ru'
        ]
        
        if not any(store in value for store in supported_stores):
            raise serializers.ValidationError(
                "URL must be from a supported store: Ozon, Wildberries, DNS, Citilink, or М.Видео"
            )
        return value

class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = ['id', 'product', 'target_price', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']