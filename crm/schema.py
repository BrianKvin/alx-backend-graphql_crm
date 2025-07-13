import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.db.models import Sum
from .models import Customer, Order, Product


# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.Int(required=True)
    total_amount = graphene.Float(required=True)
    order_date = graphene.DateTime()


# Mutations
class UpdateLowStockProducts(graphene.Mutation):
    """
    Mutation to update products with low stock (< threshold)
    """
    class Arguments:
        threshold = graphene.Int(default_value=10)
        restock_amount = graphene.Int(default_value=10)

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info, threshold, restock_amount):
        try:
            with transaction.atomic():
                low_stock_products = Product.objects.filter(stock__lt=threshold)

                if not low_stock_products.exists():
                    return UpdateLowStockProducts(
                        success=True,
                        message=f"No products with stock below {threshold}",
                        updated_products=[]
                    )

                updated_products = []
                for product in low_stock_products:
                    product.stock += restock_amount
                    product.save()
                    updated_products.append(product)

                return UpdateLowStockProducts(
                    success=True,
                    message=f"Updated {len(updated_products)} products",
                    updated_products=updated_products
                )

        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating products: {str(e)}",
                updated_products=[]
            )

class CreateCustomer(graphene.Mutation):
    """
    Mutation to create a new customer
    """
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        try:
            with transaction.atomic():
                customer = Customer.objects.create(
                    name=input.name,
                    email=input.email,
                    phone=input.get('phone')
                )
                return CreateCustomer(
                    customer=customer,
                    success=True,
                    message="Customer created successfully"
                )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                success=False,
                message=f"Error creating customer: {str(e)}"
            )

class CreateProduct(graphene.Mutation):
    """
    Mutation to create a new product
    """
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        try:
            with transaction.atomic():
                product = Product.objects.create(
                    name=input.name,
                    price=input.price,
                    stock=input.stock
                )
                return CreateProduct(
                    product=product,
                    success=True,
                    message="Product created successfully"
                )
        except Exception as e:
            return CreateProduct(
                product=None,
                success=False,
                message=f"Error creating product: {str(e)}"
            )


# Query
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello GraphQL!")

    # Customer Queries
    customers = graphene.List(
        CustomerType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    customer = graphene.Field(CustomerType, id=graphene.Int())

    # Order Queries
    orders = graphene.List(
        OrderType,
        order_date_gte=graphene.DateTime(),
        customer_id=graphene.Int(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    order = graphene.Field(OrderType, id=graphene.Int())

    # Product Queries
    products = graphene.List(
        ProductType,
        search=graphene.String(),
        min_price=graphene.Float(),
        max_price=graphene.Float(),
        first=graphene.Int(),
        skip=graphene.Int()
    )
    product = graphene.Field(ProductType, id=graphene.Int())
    low_stock_products = graphene.List(ProductType, threshold=graphene.Int(default_value=10))

    # Statistics
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()

    def resolve_customers(self, info, search=None, first=None, skip=None):
        qs = Customer.objects.all()
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(email__icontains=search)
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_orders(self, info, order_date_gte=None, customer_id=None, first=None, skip=None):
        qs = Order.objects.all()
        if order_date_gte:
            qs = qs.filter(order_date__gte=order_date_gte)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None

    def resolve_products(self, info, search=None, min_price=None, max_price=None, first=None, skip=None):
        qs = Product.objects.all()
        if search:
            qs = qs.filter(name__icontains=search)
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_low_stock_products(self, info, threshold):
        return Product.objects.filter(stock__lt=threshold)

    def resolve_total_customers(self, info):
        return Customer.objects.count()

    def resolve_total_orders(self, info):
        return Order.objects.count()

    def resolve_total_revenue(self, info):
        result = Order.objects.aggregate(total=Sum('total_amount'))
        return result['total'] or 0.0


# Mutation
class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()


# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)