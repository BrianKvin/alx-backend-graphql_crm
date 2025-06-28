#!/usr/bin/env python
"""
Database seeding script for CRM GraphQL project
Run this script to populate your database with sample data
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order


def clear_database():
    """Clear all existing data"""
    print("Clearing existing data...")
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    print("Database cleared.")


def create_customers():
    """Create sample customers"""
    print("Creating customers...")
    
    customers_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'phone': '+1234567890'
        },
        {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone': '123-456-7890'
        },
        {
            'name': 'Carol Davis',
            'email': 'carol@example.com',
            'phone': '+1987654321'
        },
        {
            'name': 'David Wilson',
            'email': 'david@example.com',
            'phone': '987-654-3210'
        },
        {
            'name': 'Eva Brown',
            'email': 'eva@example.com',
            'phone': '+1555123456'
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer.objects.create(**customer_data)
        customers.append(customer)
        print(f"Created customer: {customer.name}")
    
    return customers


def create_products():
    """Create sample products"""
    print("Creating products...")
    
    products_data = [
        {
            'name': 'Laptop Pro',
            'price': Decimal('1299.99'),
            'stock': 15
        },
        {
            'name': 'Wireless Mouse',
            'price': Decimal('29.99'),
            'stock': 50
        },
        {
            'name': 'Mechanical Keyboard',
            'price': Decimal('89.99'),
            'stock': 25
        },
        {
            'name': 'USB-C Hub',
            'price': Decimal('49.99'),
            'stock': 30
        },
        {
            'name': 'Monitor 27"',
            'price': Decimal('299.99'),
            'stock': 8
        },
        {
            'name': 'Webcam HD',
            'price': Decimal('79.99'),
            'stock': 20
        },
        {
            'name': 'Desk Lamp',
            'price': Decimal('39.99'),
            'stock': 5  # Low stock item
        },
        {
            'name': 'Bluetooth Headphones',
            'price': Decimal('159.99'),
            'stock': 12
        }
    ]
    
    products = []
    for product_data in products_data:
        product = Product.objects.create(**product_data)
        products.append(product)
        print(f"Created product: {product.name} - ${product.price}")
    
    return products


def create_orders(customers, products):
    """Create sample orders"""
    print("Creating orders...")
    
    # Order 1: Alice buys laptop and mouse
    order1 = Order.objects.create(
        customer=customers[0],  # Alice
        total_amount=Decimal('0')  # Will be calculated
    )
    order1.products.set([products[0], products[1]])  # Laptop Pro, Wireless Mouse
    order1.total_amount = order1.calculate_total()
    order1.save()
    print(f"Created order #{order1.id} for {order1.customer.name} - ${order1.total_amount}")
    
    # Order 2: Bob buys keyboard and USB hub
    order2 = Order.objects.create(
        customer=customers[1],  # Bob
        total_amount=Decimal('0')
    )
    order2.products.set([products[2], products[3]])  # Mechanical Keyboard, USB-C Hub
    order2.total_amount = order2.calculate_total()
    order2.save()
    print(f"Created order #{order2.id} for {order2.customer.name} - ${order2.total_amount}")
    
    # Order 3: Carol buys monitor and webcam
    order3 = Order.objects.create(
        customer=customers[2],  # Carol
        total_amount=Decimal('0')
    )
    order3.products.set([products[4], products[5]])  # Monitor 27", Webcam HD
    order3.total_amount = order3.calculate_total()
    order3.save()
    print(f"Created order #{order3.id} for {order3.customer.name} - ${order3.total_amount}")
    
    # Order 4: David buys multiple items
    order4 = Order.objects.create(
        customer=customers[3],  # David
        total_amount=Decimal('0')
    )
    order4.products.set([products[1], products[2], products[6]])  # Mouse, Keyboard, Desk Lamp
    order4.total_amount = order4.calculate_total()
    order4.save()
    print(f"Created order #{order4.id} for {order4.customer.name} - ${order4.total_amount}")
    
    # Order 5: Eva buys headphones
    order5 = Order.objects.create(
        customer=customers[4],  # Eva
        total_amount=Decimal('0')
    )
    order5.products.set([products[7]])  # Bluetooth Headphones
    order5.total_amount = order5.calculate_total()
    order5.save()
    print(f"Created order #{order5.id} for {order5.customer.name} - ${order5.total_amount}")


def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Clear existing data
    clear_database()
    
    # Create sample data
    customers = create_customers()
    products = create_products()
    create_orders(customers, products)
    
    print("\n" + "="*50)
    print("DATABASE SEEDING COMPLETED!")
    print("="*50)
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {Order.objects.count()} orders")
    print("\nYou can now test your GraphQL queries at:")
    print("http://localhost:8000/graphql/")
    print("\nSample query to get started:")
    print("""
{
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
      }
    }
  }
}
    """)


if __name__ == '__main__':
    main()