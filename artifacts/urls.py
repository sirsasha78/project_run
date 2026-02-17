from django.urls import path
from rest_framework.routers import DefaultRouter

from artifacts.views import CollectibleItemViewSet, UploadFileView


router = DefaultRouter()
router.register(r"collectible_item", CollectibleItemViewSet)


urlpatterns = [
    path("upload_file/", UploadFileView.as_view(), name="upload-file"),
]
urlpatterns += router.urls
