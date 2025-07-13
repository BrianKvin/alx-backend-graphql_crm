#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Set up Django environment
sys.path.append('/path/to/your/django/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

def send_order_reminders():
    """
    Query GraphQL endpoint for pending orders and log reminders
    """
    # Set up GraphQL client
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    # GraphQL query for orders within last 7 days
    query = gql("""
        query GetRecentOrders($dateFrom: DateTime!) {
            orders(orderDate_Gte: $dateFrom) {
                edges {
                    node {
                        id
                        orderDate
                        customer {
                            email
                        }
                    }
                }
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"dateFrom": seven_days_ago.isoformat()})
        
        # Process results and log
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"\n{timestamp} - Order Reminders Processing:\n")
            
            if result['orders']['edges']:
                for edge in result['orders']['edges']:
                    order = edge['node']
                    order_id = order['id']
                    customer_email = order['customer']['email']
                    
                    log_entry = f"{timestamp} - Order ID: {order_id}, Customer: {customer_email}\n"
                    log_file.write(log_entry)
            else:
                log_file.write(f"{timestamp} - No pending orders found\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} - Error processing reminders: {str(e)}\n")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_order_reminders()