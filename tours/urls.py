# from django.urls import path
# from .views import TourPackageListCreateView, TourPackageDetailView, CountryListCreateView

# urlpatterns = [
#     path("tours/", TourPackageListCreateView.as_view(), name="tour_list_create"),
#     path("tours/<int:pk>/", TourPackageDetailView.as_view(), name="tour_detail"),
#     path("countries/", CountryListCreateView.as_view(), name="country_list"),
# ]

# from django.urls import path
# from .views import TourPackageListCreateView, TourPackageDetailView, CountryListCreateView,TourPlanListCreateView, TourPlanDetailView

# urlpatterns = [
#     path("tours/", TourPackageListCreateView.as_view(), name="tour_list_create"),
#     path("tours/<int:pk>/", TourPackageDetailView.as_view(), name="tour_detail"),
#     path("tours/<int:pk>/activate/", TourPackageDetailView.as_view(), name="tour_activate"),
#     path("countries/", CountryListCreateView.as_view(), name="country_list"),
#     path("tours/<int:package_id>/plans/", TourPlanListCreateView.as_view(), name="tour_plan_list_create"),
#     path("tours/plans/<int:pk>/", TourPlanDetailView.as_view(), name="tour_plan_detail"),
# ]

from django.urls import path
from .views import ActivityCreateView, AssignHighlightToCountryView, CategoryCreateView, CountryListCreateView, CreateHighlightView, TourImageListCreateView, TourPackageByCountryView, TourPackageListCreateView, TourPackageDetailView, TourPlanListCreateView, TourPlanDetailView, UpdateCountryImageView, WhenToGoDetailView, WhenToGoListCreateView
from .views import (
    CategoryListView,
    ActivityListView,
    CustomPackageCreateView,
    CustomPackageListView,
    CustomPackageDetailView,
    CustomPackageDeleteView,
    AddActivityToPackageView,
    RemoveActivityFromPackageView
)

urlpatterns = [
    # Countries
    path("countries/", CountryListCreateView.as_view(), name="country_list_create"),
    path("countries/<int:pk>/image/", UpdateCountryImageView.as_view(), name="update-country-image"),
     path("countries/highlights/", CreateHighlightView.as_view(), name="create-highlight"),
     path("countries/<int:country_id>/assign/", AssignHighlightToCountryView.as_view(), name="assign-highlight"),

    
    # Tour Packages
    path("tours/", TourPackageListCreateView.as_view(), name="tour_package_list_create"),
    path("tours/<int:pk>/", TourPackageDetailView.as_view(), name="tour_package_detail"),
    path("tours/<int:pk>/activate/", TourPackageDetailView.as_view(), name="tour_activate"),
    path("tours/<int:pk>/update/", TourPackageDetailView.as_view(), name="tour_package_update"),
    path("tours/<int:pk>/delete/", TourPackageDetailView.as_view(), name="tour_package_delete"),
     path("tours/country/<int:country_id>/", TourPackageByCountryView.as_view(), name="tour-packages-by-country"),
    path('tours/<int:package_id>/images/', TourImageListCreateView.as_view(), name='car-image-list-create'),

    # Tour Plans
    path("tours/<int:package_id>/plans/", TourPlanListCreateView.as_view(), name="tour_plan_list_create"),
    path("tours/plans/<int:pk>/", TourPlanDetailView.as_view(), name="tour_plan_detail"),
    path("tours/plans/<int:pk>/update/", TourPlanDetailView.as_view(), name="tour_plan_update"),
    path("tours/plans/<int:pk>/delete/", TourPlanDetailView.as_view(), name="tour_plan_delete"),

    # when to go
    path('when-to-go/', WhenToGoListCreateView.as_view(), name='when-to-go-list-create'),
    path('when-to-go/<int:pk>/', WhenToGoDetailView.as_view(), name='when-to-go-detail'),

    # custom packages

    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('activities/', ActivityListView.as_view(), name='activity-list'),
    path('activities/create/', ActivityCreateView.as_view(), name='activity-create'),

    #  Custom Packages CRUD
    path('packages/', CustomPackageCreateView.as_view(), name='package-create'),
    path('packages/list/', CustomPackageListView.as_view(), name='package-list'),
    path('packages/<int:pk>/', CustomPackageDetailView.as_view(), name='package-detail'),
    path('packages/<int:pk>/delete/', CustomPackageDeleteView.as_view(), name='package-delete'),

    #  Manage activities inside a package
    path('packages/<int:pk>/add-activity/', AddActivityToPackageView.as_view(), name='package-add-activity'),
    path('packages/<int:package_pk>/remove-activity/<int:activity_pk>/', RemoveActivityFromPackageView.as_view(), name='package-remove-activity'),
]
