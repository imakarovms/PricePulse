from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from .models import TrackedProduct, PriceAlert
from .serializers import TrackedProductSerializer, PriceAlertSerializer
from .parsers import get_parser
from .tasks import update_product_price

class TrackedProductViewSet(viewsets.ModelViewSet):
    serializer_class = TrackedProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TrackedProduct.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new tracked product with automatic parsing"""
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if product already exists for this user
            if TrackedProduct.objects.filter(user=request.user, url=url).exists():
                return Response(
                    {'error': 'Product is already being tracked'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get parser and parse the product
            parser = get_parser(url)
            parsed_data = parser(url)
            
            if not parsed_data.get('price'):
                return Response(
                    {'error': 'Could not extract price from the provided URL'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the tracked product
            with transaction.atomic():
                product = TrackedProduct.objects.create(
                    user=request.user,
                    url=url,
                    title=parsed_data.get('title', 'Unknown Product'),
                    brand=parsed_data.get('brand', ''),
                    current_price=parsed_data['price'],
                    is_in_stock=parsed_data.get('in_stock', True)
                )
                
                # Add initial price to history
                product.add_price_to_history(product.current_price)
                product.save()
            
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Failed to parse product: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """Manually trigger price update for a product"""
        product = self.get_object()
        
        try:
            update_product_price.delay(product.id)
            return Response({'message': 'Price update scheduled'})
        except Exception as e:
            return Response(
                {'error': f'Failed to schedule update: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        """Get price history for a product"""
        product = self.get_object()
        return Response({
            'product_id': product.id,
            'product_title': product.title,
            'price_history': product.price_history
        })

class PriceAlertViewSet(viewsets.ModelViewSet):
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)