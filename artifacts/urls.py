from rest_framework.routers import DefaultRouter

from artifacts.views import CollectibleItemViewSet


router = DefaultRouter()
router.register(r"collectible_item", CollectibleItemViewSet)
