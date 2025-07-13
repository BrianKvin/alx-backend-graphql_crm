from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to get report data
        query = gql("""
            query GetCRMStats {
                totalCustomers
                totalOrders
                totalRevenue
            }
        """)
        
        result = client.execute(query)
        
        # Extract data
        total_customers = result.get('totalCustomers', 0)
        total_orders = result.get('totalOrders', 0)
        total_revenue = result.get('totalRevenue', 0.0)
        
        # Format report
        report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n"
        
        # Write to log file
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(report_line)
        
        return f"Report generated successfully: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
        
    except Exception as e:
        error_line = f"{timestamp} - Error generating report: {str(e)}\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_line)
        
        return f"Error generating report: {str(e)}"

@shared_task
def cleanup_old_logs():
    """
    Optional task to cleanup old log files
    """
    import os
    from datetime import datetime, timedelta
    
    log_files = [
        '/tmp/crm_report_log.txt',
        '/tmp/crm_heartbeat_log.txt',
        '/tmp/low_stock_updates_log.txt',
        '/tmp/order_reminders_log.txt',
        '/tmp/customer_cleanup_log.txt'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Read all lines
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                # Keep only lines from last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                filtered_lines = []
                
                for line in lines:
                    # Try to extract date from line
                    try:
                        date_str = line[:19]  # First 19 characters should be date
                        line_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        if line_date > thirty_days_ago:
                            filtered_lines.append(line)
                    except ValueError:
                        # If date parsing fails, keep the line
                        filtered_lines.append(line)
                
                # Write back filtered lines
                with open(log_file, 'w') as f:
                    f.writelines(filtered_lines)
                    
            except Exception as e:
                print(f"Error cleaning {log_file}: {str(e)}")
    
    return "Log cleanup completed"