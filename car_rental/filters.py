import django_filters
from .models import Car

class CarFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains') 
    brand = django_filters.CharFilter(lookup_expr='icontains')
    year = django_filters.NumberFilter()
    mileage = django_filters.NumberFilter()
    fuel_type = django_filters.CharFilter()
    transmission = django_filters.CharFilter()
    seats = django_filters.NumberFilter()
    luggage_capacity = django_filters.NumberFilter()
    price_per_day = django_filters.RangeFilter()  
    is_available = django_filters.BooleanFilter()

    class Meta:
        model = Car
        fields = ['name', 'brand', 'year', 'mileage', 'fuel_type', 'transmission', 'seats', 'luggage_capacity', 'price_per_day', 'is_available']
