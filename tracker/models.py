from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import json

User = get_user_model()

class TrackedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_products')
    url = models.URLField(max_length=500, validators=[URLValidator()])
    title = models.CharField(max_length=300)
    brand = models.CharField(max_length=100, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price_history = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'url']
    
    def __str__(self):
        return f"{self.title} - {self.current_price}₽"
    
    def add_price_to_history(self, price):
        """Add current price to history with timestamp"""
        if not isinstance(self.price_history, list):
            self.price_history = []
        
        from datetime import datetime
        self.price_history.append({
            'price': float(price),
            'timestamp': datetime.now().isoformat()
        })
    
    def save(self, *args, **kwargs):
        # Add current price to history when price changes
        if self.pk and self.current_price != self.previous_price:
            self.add_price_to_history(self.current_price)
        
        super().save(*args, **kwargs)
        self.previous_price = self.current_price

class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(TrackedProduct, on_delete=models.CASCADE, related_name='alerts')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Alert for {self.product.title} at {self.target_price}₽"