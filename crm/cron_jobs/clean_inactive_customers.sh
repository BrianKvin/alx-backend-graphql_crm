#!/bin/bash

# Navigate to the Django project directory
cd /path/to/your/django/project

# Execute Django management command to delete inactive customers
DELETED_COUNT=$(python manage.py shell << 'EOF'
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the last year
inactive_customers = Customer.objects.filter(
    orders__order_date__lt=one_year_ago
).distinct() | Customer.objects.filter(orders__isnull=True)

# Count and delete
count = inactive_customers.count()
inactive_customers.delete()

print(count)
EOF
)

# Log the result with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt