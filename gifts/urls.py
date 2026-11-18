from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (GiftViewSet, InterestViewSet, PersonalityViewSet, OccasionViewSet)

router = DefaultRouter()
router.register('gifts', GiftViewSet, basename='gift')
router.register('interests', InterestViewSet)
router.register('personalities', PersonalityViewSet)
router.register('occasions', OccasionViewSet)

urlpatterns = router.urls