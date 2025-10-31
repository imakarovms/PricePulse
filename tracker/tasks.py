from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import TrackedProduct, PriceAlert
from tracker.parsers import get_parser
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def update_product_price(product_id):
    """Update price for a single product"""
    try:
        product = TrackedProduct.objects.get(id=product_id)
        old_price = product.current_price
        
        # Get parser and parse current data
        parser = get_parser(product.url)
        data = parser.get_data()
        
        new_price = data.get('price')
        if new_price is None:
            logger.error(f"Could not extract price for product {product_id}")
            return False
        
        # Update product data
        product.current_price = new_price
        product.title = data.get('title', product.title)
        product.brand = data.get('brand', product.brand)
        product.is_in_stock = data.get('in_stock', product.is_in_stock)
        
        # Add to price history
        product.add_price_to_history(new_price)
        product.save()
        
        # Check for price drop alerts
        if new_price < old_price:
            # Check if user has alerts for this product
            alerts = PriceAlert.objects.filter(
                product=product, 
                is_active=True, 
                target_price__gte=new_price
            )
            
            for alert in alerts:
                send_price_drop_alert.delay(alert.id, old_price, new_price)
        
        logger.info(f"Updated price for product {product_id}: {old_price} -> {new_price}")
        return True
        
    except TrackedProduct.DoesNotExist:
        logger.error(f"Product {product_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        return False

@shared_task
def check_all_prices():
    products = TrackedProduct.objects.all()
    scheduled_count = 0
    for product in products:
        try:
            update_product_price.delay(product.id)
            scheduled_count += 1
        except Exception as e:
            logger.error(f"Failed to schedule update for product {product.id}: {str(e)}")
    logger.info(f"Scheduled price updates for {scheduled_count} products")
    return scheduled_count

