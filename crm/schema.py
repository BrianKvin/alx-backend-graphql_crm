import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import re

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# GraphQL Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        interfaces = (graphene.relay.Node,)


# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Mutation Response Types
class CustomerMutationResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)


class BulkCustomerMutationResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()


class ProductMutationResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)


class OrderMutationResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)


# Mutation Classes
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CustomerMutationResponse

    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:
            return True
        
        patterns = [
            r'^\+?1?\d{9,15}$',  # International format
            r'^\d{3}-\d{3}-\d{4}$'  # US format with dashes
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)

    def mutate(self, info, input):
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                return CustomerMutationResponse(
                    success=False,
                    errors=["Email already exists"]
                )
            
            # Validate phone format if provided
            if input.phone and not self.validate_phone(input.phone):
                return CustomerMutationResponse(
                    success=False,
                    errors=["Invalid phone number format"]
                )
            
            # Create customer
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            
            return CustomerMutationResponse(
                customer=customer,
                message="Customer created successfully",
                success=True
            )
            
        except Exception as e:
            return CustomerMutationResponse(
                success=False,
                errors=[str(e)]
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCustomerMutationResponse

    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {i+1}: Email already exists")
                        continue
                    
                    # Validate phone format if provided
                    if customer_data.phone and not CreateCustomer.validate_phone(customer_data.phone):
                        errors.append(f"Customer {i+1}: Invalid phone number format")
                        continue
                    
                    # Create customer
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    created_customers.append(customer)
                    
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCustomerMutationResponse(
            customers=created_customers,
            errors=errors,
            success_count=len(created_customers),
            error_count=len(errors)
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = ProductMutationResponse

    def mutate(self, info, input):
        try:
            # Validate price is positive
            if input.price <= 0:
                return ProductMutationResponse(
                    success=False,
                    errors=["Price must be positive"]
                )
            
            # Validate stock is non-negative
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                return ProductMutationResponse(
                    success=False,
                    errors=["Stock cannot be negative"]
                )
            
            # Create product
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            
            return ProductMutationResponse(
                product=product,
                message="Product created successfully",
                success=True
            )
            
        except Exception as e:
            return ProductMutationResponse(
                success=False,
                errors=[str(e)]
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = OrderMutationResponse

    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                return OrderMutationResponse(
                    success=False,
                    errors=["Invalid customer ID"]
                )
            
            # Validate products exist
            if not input.product_ids:
                return OrderMutationResponse(
                    success=False,
                    errors=["At least one product must be selected"]
                )
            
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                return OrderMutationResponse(
                    success=False,
                    errors=["One or more invalid product IDs"]
                )
            
            # Calculate total amount
            total_amount = sum(product.price for product in products)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount,
                order_date=input.order_date or timezone.now()
            )
            
            # Associate products
            order.products.set(products)
            
            return OrderMutationResponse(
                order=order,
                message="Order created successfully",
                success=True
            )
            
        except Exception as e:
            return OrderMutationResponse(
                success=False,
                errors=[str(e)]
            )


# Query Class
class Query(graphene.ObjectType):
    # Basic greeting query
    hello = graphene.String()
    
    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    
    # Filtered list queries
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None


# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()