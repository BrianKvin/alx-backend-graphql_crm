import django_filters
from django.db import models
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """Filter class for Customer model with various search options"""
    
    # Case-insensitive partial match for name
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    # Case-insensitive partial match for email
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    
    # Date range filters for creation date
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Custom filter for phone number pattern (starts with +1)
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at_gte', 'created_at_lte', 'phone_pattern']
    
    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter to match phone numbers starting with specific pattern"""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    """Filter class for Product model with price and stock filtering"""
    
    # Case-insensitive partial match for name
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    # Price range filters
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Stock range filters
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    stock = django_filters.NumberFilter(field_name='stock', lookup_expr='exact')
    
    # Custom filter for low stock products
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    class Meta:
        model = Product
        fields = ['name', 'price_gte', 'price_lte', 'stock_gte', 'stock_lte', 'stock', 'low_stock']
    
    def filter_low_stock(self, queryset, name, value):
        """Filter products with stock less than 10"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    """Filter class for Order model with customer and product lookups"""
    
    # Total amount range filters
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Order date range filters
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')
    
    # Filter by customer name (related field lookup)
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    
    # Filter by product name (related field lookup through many-to-many)
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    
    # Filter orders that include a specific product ID
    product_id = django_filters.NumberFilter(field_name='products__id', lookup_expr='exact')
    
    class Meta:
        model = Order
        fields = [
            'total_amount_gte', 'total_amount_lte',
            'order_date_gte', 'order_date_lte',
            'customer_name', 'product_name', 'product_id'
        ]