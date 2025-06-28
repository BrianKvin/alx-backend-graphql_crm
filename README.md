# ALX Backend GraphQL CRM

A Customer Relationship Management (CRM) system built with Django and GraphQL using Graphene-Django.

## Features

- **GraphQL API** with queries and mutations
- **Customer Management** with validation
- **Product Management** with stock tracking
- **Order Management** with automatic total calculation
- **Advanced Filtering** using django-filter
- **Bulk Operations** with error handling
- **Admin Interface** for easy data management

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd alx-backend-graphql_crm
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Seed Database with Sample Data
```bash
python seed_db.py
```

### 7. Run Development Server
```bash
python manage.py runserver
```

### 8. Access GraphQL Interface
Visit: http://localhost:8000/graphql/

## GraphQL Schema

### Queries

#### Basic Query
```graphql
{
  hello
}
```

#### Get All Customers
```graphql
{
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
        createdAt
      }
    }
  }
}
```

#### Get All Products
```graphql
{
  allProducts {
    edges {
      node {
        id
        name
        price
        stock
        createdAt
      }
    }
  }
}
```

#### Get All Orders
```graphql
{
  allOrders {
    edges {
      node {
        id
        customer {
          name
          email
        }
        products {
          name
          price
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

### Mutations

#### Create Customer
```graphql
mutation {
  createCustomer(input: {
    name: "Alice Johnson"
    email: "alice@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
    success
    errors
  }
}
```

#### Bulk Create Customers
```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob Smith", email: "bob@example.com", phone: "123-456-7890" }
    { name: "Carol Davis", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
    successCount
    errorCount
  }
}
```

#### Create Product
```graphql
mutation {
  createProduct(input: {
    name: "Laptop Pro"
    price: "1299.99"
    stock: 15
  }) {
    product {
      id
      name
      price
      stock
    }
    message
    success
    errors
  }
}
```

#### Create Order
```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
    message
    success
    errors
  }
}
```

### Filtering

#### Filter Customers by Name
```graphql
{
  allCustomers(filter: { nameIcontains: "Alice" }) {
    edges {
      node {
        id
        name
        email
      }
    }
  }
}
```

#### Filter Products by Price Range
```graphql
{
  allProducts(filter: { priceGte: "100", priceLte: "1000" }) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

#### Filter Orders by Customer Name
```graphql
{
  allOrders(filter: { customerName: "Alice" }) {
    edges {
      node {
        id
        customer {
          name
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

#### Filter Products with Low Stock
```graphql
{
  allProducts(filter: { lowStock: true }) {
    edges {
      node {
        id
        name
        stock
        price
      }
    }
  }
}
```

## Models

### Customer
- `name`: CharField (max_length=100)
- `email`: EmailField (unique=True)
- `phone`: CharField (optional, validated format)
- `created_at`: DateTimeField (auto_now_add=True)
- `updated_at`: DateTimeField (auto_now=True)

### Product
- `name`: CharField (max_length=100)
- `price`: DecimalField (max_digits=10, decimal_places=2)
- `stock`: PositiveIntegerField (default=0)
- `created_at`: DateTimeField (auto_now_add=True)
- `updated_at`: DateTimeField (auto_now=True)

### Order
- `customer`: ForeignKey to Customer
- `products`: ManyToManyField to Product
- `total_amount`: DecimalField (calculated automatically)
- `order_date`: DateTimeField (auto_now_add=True)
- `created_at`: DateTimeField (auto_now_add=True)
- `updated_at`: DateTimeField (auto_now=True)

## Validation

### Customer Validation
- Email must be unique
- Phone number format: `+1234567890` or `123-456-7890`

### Product Validation
- Price must be positive
- Stock cannot be negative

### Order Validation
- Customer must exist
- All products must exist
- At least one product must be selected
- Total amount calculated automatically

## Admin Interface

Access the admin interface at: http://localhost:8000/admin/

Features:
- Customer management with search and filters
- Product management with inline editing
- Order management with product associations
- Readonly total amount calculation

## Testing

Run tests with:
```bash
python manage.py test
```

## Project Structure

```
alx-backend-graphql_crm/
├── manage.py
├── requirements.txt
├── README.md
├── seed_db.py
├── alx-backend-graphql_crm/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── schema.py
└── crm/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── schema.py
    ├── filters.py
    ├── tests.py
    └── migrations/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.