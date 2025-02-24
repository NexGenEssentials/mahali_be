from django.urls import path
from .views import CarImageListCreateView, CarImageRetrieveDeleteView, CarListCreateView, CarDetailView, CheckAvailabilityView,AddFeatureToCarView, FeatureCreateView

urlpatterns = [
    path('cars/', CarListCreateView.as_view(), name='car-list-create'),
    path('cars/<int:pk>/', CarDetailView.as_view(), name='car-detail'),
    path('cars/check-availability/', CheckAvailabilityView.as_view(), name='check-availability'),
    path('cars/features/', FeatureCreateView.as_view(), name='add new feature'),
    path('cars/<int:car_id>/add-features/', AddFeatureToCarView.as_view(), name='feature-detail'),
    path('cars/<int:car_id>/images/', CarImageListCreateView.as_view(), name='car-image-list-create'),
    path('cars/<int:car_id>/images/<int:image_id>/', CarImageRetrieveDeleteView.as_view(), name='car-image-detail'),
]
