import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM health
    """
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    heartbeat_message = f"{timestamp} CRM is alive\n"
    
    # Append to heartbeat log
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(heartbeat_message)
    
    # Optional: Test GraphQL endpoint
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Simple hello query
        query = gql("""
            query {
                hello
            }
        """)
        
        result = client.execute(query)
        
        # Log GraphQL response
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} GraphQL endpoint responsive: {result.get('hello', 'No response')}\n")
            
    except Exception as e:
        # Log GraphQL error
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} GraphQL endpoint error: {str(e)}\n")

def update_low_stock():
    """
    Update low stock products using GraphQL mutation
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute mutation to update low stock products
        mutation = gql("""
            mutation UpdateLowStockProducts {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        name
                        stock
                    }
                }
            }
        """)
        
        result = client.execute(mutation)
        
        # Log the results
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"\n{timestamp} - Low Stock Update:\n")
            
            if result['updateLowStockProducts']['success']:
                updated_products = result['updateLowStockProducts']['updatedProducts']
                
                if updated_products:
                    for product in updated_products:
                        log_file.write(f"{timestamp} - Updated: {product['name']}, New Stock: {product['stock']}\n")
                else:
                    log_file.write(f"{timestamp} - No products needed restocking\n")
            else:
                log_file.write(f"{timestamp} - Update failed: {result['updateLowStockProducts']['message']}\n")
                
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} - Error updating low stock: {str(e)}\n")