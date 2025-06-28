from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class Customer(models.Model):
    """Customer model for CRM system"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$',
        message="Phone number must be entered in the format: '+999999999' or '999-999-9999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Product(models.Model):
    """Product model for CRM system"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def clean(self):
        if self.price <= 0:
            raise ValidationError('Price must be positive')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Order(models.Model):
    """Order model for CRM system"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']

    def calculate_total(self):
        """Calculate total amount based on associated products"""
        return sum(product.price for product in self.products.all())

    def save(self, *args, **kwargs):
        # Save first to get an ID if this is a new object
        super().save(*args, **kwargs)
        # Calculate and update total amount
        self.total_amount = self.calculate_total()
        if self.total_amount != self.calculate_total():
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - ${self.total_amount}"