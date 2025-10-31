from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackedProductViewSet, PriceAlertViewSet
from . import views

router = DefaultRouter()
router.register(r'tracked-products', TrackedProductViewSet, basename='trackedproduct')
router.register(r'price-alerts', PriceAlertViewSet, basename='pricealert')

urlpatterns = [
    path('', include(router.urls)),
    path('parse/', views.simple_parser_view, name='simple-parser'),
]
18126