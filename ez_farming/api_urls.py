from django.urls import path, include
from rest_framework.routers import DefaultRouter

# User
from user.views import UserViewSet

# Meat Module
from ezmeat.views import MeatAnimalViewSet, WeightRecordViewSet, SlaughterRecordViewSet

# Dairy Module
from ezdairy.views import DairyAnimalViewSet, MilkProductionViewSet, LactationViewSet

# Animal Basics
from ezanimal.views import AnimalTypeViewSet, BreedViewSet

# Health and Feed
from ezcore.health_and_feed.views import (
    AnimalHealthViewSet, VaccinationViewSet, FeedTypeViewSet,
    FeedingScheduleViewSet, FeedingScheduleItemViewSet, FeedingRecordViewSet
)

# Inventory and Sales
from ezcore.inventory_and_sales.views import (
    InventoryItemViewSet, InventoryTransactionViewSet,
    SaleViewSet, SaleItemViewSet, ExpenseViewSet
)

# Create main router for core entities
router = DefaultRouter()

# User
router.register(r'users', UserViewSet, basename='user')

# Meat module
router.register(r'meat-animals', MeatAnimalViewSet, basename='meat-animal')
router.register(r'weight-records', WeightRecordViewSet, basename='weight-record')
router.register(r'slaughter-records', SlaughterRecordViewSet, basename='slaughter-record')

# Dairy module
router.register(r'dairy-animals', DairyAnimalViewSet, basename='dairy-animal')
router.register(r'milk-productions', MilkProductionViewSet, basename='milk-production')
router.register(r'lactations', LactationViewSet, basename='lactation')

# Animal basics
router.register(r'animal-types', AnimalTypeViewSet, basename='animal-type')
router.register(r'breeds', BreedViewSet, basename='breed')

# Health & Feed
router.register(r'health-records', AnimalHealthViewSet, basename='animal-health')
router.register(r'vaccinations', VaccinationViewSet, basename='vaccination')
router.register(r'feed-types', FeedTypeViewSet, basename='feed-type')
router.register(r'feeding-schedules', FeedingScheduleViewSet, basename='feeding-schedule')
router.register(r'feeding-schedule-items', FeedingScheduleItemViewSet, basename='feeding-schedule-item')
router.register(r'feeding-records', FeedingRecordViewSet, basename='feeding-record')

# Inventory & Sales
router.register(r'inventory-items', InventoryItemViewSet, basename='inventory-item')
router.register(r'inventory-transactions', InventoryTransactionViewSet, basename='inventory-transaction')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'sale-items', SaleItemViewSet, basename='sale-item')
router.register(r'expenses', ExpenseViewSet, basename='expense')


urlpatterns = [
    path('', include(router.urls)),
]
