"""
Data Processor Module
Handles data cleaning, validation, and analysis operations
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict


# ============================================
# Task 2.1: Sales Summary Calculator
# ============================================

def calculate_total_revenue(transactions: List[Dict]) -> float:
    """
    Calculates total revenue from all transactions

    Args:
        transactions: List of transaction dictionaries

    Returns:
        float (total revenue)

    Expected Output: Single number representing sum of (Quantity * UnitPrice)
    Example: 1545000.50
    """
    
    total_revenue = 0.0
    
    for transaction in transactions:
        try:
            quantity = transaction.get('Quantity', 0)
            unit_price = transaction.get('UnitPrice', 0.0)
            
            # Ensure proper types
            if isinstance(quantity, str):
                quantity = float(quantity.replace(',', ''))
            if isinstance(unit_price, str):
                unit_price = float(unit_price.replace(',', ''))
            
            total_revenue += quantity * unit_price
            
        except (ValueError, TypeError):
            # Skip transactions with invalid data
            continue
    
    return round(total_revenue, 2)


def region_wise_sales(transactions: List[Dict]) -> Dict[str, Dict]:
    """
    Analyzes sales by region

    Args:
        transactions: List of transaction dictionaries

    Returns:
        dictionary with region statistics

    Expected Output Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        'South': {...},
        ...
    }

    Requirements:
    - Calculate total sales per region
    - Count transactions per region
    - Calculate percentage of total sales
    - Sort by total_sales in descending order
    """
    
    region_data = {}
    total_all_sales = 0.0
    
    # First pass: collect data
    for transaction in transactions:
        try:
            region = transaction.get('Region', '').strip()
            if not region:
                continue
                
            quantity = transaction.get('Quantity', 0)
            unit_price = transaction.get('UnitPrice', 0.0)
            
            # Ensure proper types
            if isinstance(quantity, str):
                quantity = float(quantity.replace(',', ''))
            if isinstance(unit_price, str):
                unit_price = float(unit_price.replace(',', ''))
            
            revenue = quantity * unit_price
            total_all_sales += revenue
            
            if region not in region_data:
                region_data[region] = {
                    'total_sales': 0.0,
                    'transaction_count': 0
                }
            
            region_data[region]['total_sales'] += revenue
            region_data[region]['transaction_count'] += 1
            
        except (ValueError, TypeError):
            continue
    
    # Second pass: calculate percentages and sort
    result = {}
    for region, data in region_data.items():
        percentage = 0.0
        if total_all_sales > 0:
            percentage = round((data['total_sales'] / total_all_sales) * 100, 2)
        
        result[region] = {
            'total_sales': round(data['total_sales'], 2),
            'transaction_count': data['transaction_count'],
            'percentage': percentage
        }
    
    # Sort by total_sales in descending order
    sorted_result = dict(sorted(
        result.items(),
        key=lambda x: x[1]['total_sales'],
        reverse=True
    ))
    
    return sorted_result


def top_selling_products(transactions: List[Dict], n: int = 5) -> List[Tuple]:
    """
    Finds top n products by total quantity sold

    Args:
        transactions: List of transaction dictionaries
        n: Number of top products to return (default: 5)

    Returns:
        list of tuples

    Expected Output Format:
    [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Mouse', 38, 19000.0),
        ...
    ]

    Requirements:
    - Aggregate by ProductName
    - Calculate total quantity sold
    - Calculate total revenue for each product
    - Sort by TotalQuantity descending
    - Return top n products
    """
    
    product_data = {}
    
    for transaction in transactions:
        try:
            product_name = transaction.get('ProductName', '').strip()
            if not product_name:
                continue
                
            quantity = transaction.get('Quantity', 0)
            unit_price = transaction.get('UnitPrice', 0.0)
            
            # Ensure proper types
            if isinstance(quantity, str):
                quantity = int(float(quantity.replace(',', '')))
            if isinstance(unit_price, str):
                unit_price = float(unit_price.replace(',', ''))
            
            if product_name not in product_data:
                product_data[product_name] = {
                    'total_quantity': 0,
                    'total_revenue': 0.0
                }
            
            product_data[product_name]['total_quantity'] += quantity
            product_data[product_name]['total_revenue'] += quantity * unit_price
            
        except (ValueError, TypeError):
            continue
    
    # Convert to list of tuples and sort
    product_list = []
    for product_name, data in product_data.items():
        product_list.append((
            product_name,
            data['total_quantity'],
            round(data['total_revenue'], 2)
        ))
    
    # Sort by total quantity in descending order
    product_list.sort(key=lambda x: x[1], reverse=True)
    
    # Return top n products
    return product_list[:n]


def customer_analysis(transactions: List[Dict]) -> Dict[str, Dict]:
    """
    Analyzes customer purchase patterns

    Args:
        transactions: List of transaction dictionaries

    Returns:
        dictionary of customer statistics

    Expected Output Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        'C002': {...},
        ...
    }

    Requirements:
    - Calculate total amount spent per customer
    - Count number of purchases
    - Calculate average order value
    - List unique products bought
    - Sort by total_spent descending
    """
    
    customer_data = {}
    
    for transaction in transactions:
        try:
            customer_id = transaction.get('CustomerID', '').strip()
            product_name = transaction.get('ProductName', '').strip()
            
            if not customer_id or not product_name:
                continue
                
            quantity = transaction.get('Quantity', 0)
            unit_price = transaction.get('UnitPrice', 0.0)
            
            # Ensure proper types
            if isinstance(quantity, str):
                quantity = float(quantity.replace(',', ''))
            if isinstance(unit_price, str):
                unit_price = float(unit_price.replace(',', ''))
            
            amount_spent = quantity * unit_price
            
            if customer_id not in customer_data:
                customer_data[customer_id] = {
                    'total_spent': 0.0,
                    'purchase_count': 0,
                    'products_bought': set()
                }
            
            customer_data[customer_id]['total_spent'] += amount_spent
            customer_data[customer_id]['purchase_count'] += 1
            customer_data[customer_id]['products_bought'].add(product_name)
            
        except (ValueError, TypeError):
            continue
    
    # Calculate averages and convert sets to lists
    result = {}
    for customer_id, data in customer_data.items():
        avg_order_value = 0.0
        if data['purchase_count'] > 0:
            avg_order_value = round(data['total_spent'] / data['purchase_count'], 2)
        
        result[customer_id] = {
            'total_spent': round(data['total_spent'], 2),
            'purchase_count': data['purchase_count'],
            'avg_order_value': avg_order_value,
            'products_bought': sorted(list(data['products_bought']))
        }
    
    # Sort by total_spent in descending order
    sorted_result = dict(sorted(
        result.items(),
        key=lambda x: x[1]['total_spent'],
        reverse=True
    ))
    
    return sorted_result


# ============================================
# Task 2.2: Date-based Analysis
# ============================================

def daily_sales_trend(transactions: List[Dict]) -> Dict[str, Dict]:
    """
    Analyzes sales trends by date

    Args:
        transactions: List of transaction dictionaries

    Returns:
        dictionary sorted by date

    Expected Output Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        '2024-12-02': {...},
        ...
    }

    Requirements:
    - Group by date
    - Calculate daily revenue
    - Count daily transactions
    - Count unique customers per day
    - Sort chronologically
    """
    
    daily_data = {}
    
    for transaction in transactions:
        try:
            date = transaction.get('Date', '').strip()
            customer_id = transaction.get('CustomerID', '').strip()
            
            if not date:
                continue
                
            quantity = transaction.get('Quantity', 0)
            unit_price = transaction.get('UnitPrice', 0.0)
            
            # Ensure proper types
            if isinstance(quantity, str):
                quantity = float(quantity.replace(',', ''))
            if isinstance(unit_price, str):
                unit_price = float(unit_price.replace(',', ''))
            
            revenue = quantity * unit_price
            
            if date not in daily_data:
                daily_data[date] = {
                    'revenue': 0.0,
                    'transaction_count': 0,
                    'unique_customers': set()
                }
            
            daily_data[date]['revenue'] += revenue
            daily_data[date]['transaction_count'] += 1
            if customer_id:
                daily_data[date]['unique_customers'].add(customer_id)
            
        except (ValueError, TypeError):
            continue
    
    # Prepare final result
    result = {}
    for date, data in daily_data.items():
        result[date] = {
            'revenue': round(data['revenue'], 2),
            'transaction_count': data['transaction_count'],
            'unique_customers': len(data['unique_customers'])
        }
    
    # Sort chronologically
    sorted_result = dict(sorted(result.items()))
    
    return sorted_result


def find_peak_sales_day(transactions: List[Dict]) -> Tuple[str, float, int]:
    """
    Identifies the date with highest revenue

    Args:
        transactions: List of transaction dictionaries

    Returns:
        tuple (date, revenue, transaction_count)

    Expected Output Format:
    ('2024-12-15', 185000.0, 12)
    """
    
    daily_trend = daily_sales_trend(transactions)
    
    if not daily_trend:
        return ('', 0.0, 0)
    
    # Find the date with maximum revenue
    peak_date = max(daily_trend.items(), key=lambda x: x[1]['revenue'])
    
    return (
        peak_date[0],  # date
        peak_date[1]['revenue'],  # revenue
        peak_date[1]['transaction_count']  # transaction_count
    )


# ============================================
# Task 2.3: Product Performance
# ============================================

def low_performing_products(transactions: List[Dict], threshold: int = 10) -> List[Tuple]:
    """
    Identifies products with low sales

    Args:
        transactions: List of transaction dictionaries
        threshold: Minimum quantity threshold (default: 10)

    Returns:
        list of tuples

    Expected Output Format:
    [
        ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Headphones', 7, 10500.0),
        ...
    ]

    Requirements:
    - Find products with total quantity < threshold
    - Include total quantity and revenue
    - Sort by TotalQuantity ascending
    """
    
    product_data = {}
    
    # First, aggregate all product data
    for transaction in transactions:
        try:
            product_name = transaction.get('ProductName', '').strip()
            if not product_name:
                continue
                
            quantity = transaction.get('Quantity', 0)
            unit_price = transaction.get('UnitPrice', 0.0)
            
            # Ensure proper types
            if isinstance(quantity, str):
                quantity = int(float(quantity.replace(',', '')))
            if isinstance(unit_price, str):
                unit_price = float(unit_price.replace(',', ''))
            
            if product_name not in product_data:
                product_data[product_name] = {
                    'total_quantity': 0,
                    'total_revenue': 0.0
                }
            
            product_data[product_name]['total_quantity'] += quantity
            product_data[product_name]['total_revenue'] += quantity * unit_price
            
        except (ValueError, TypeError):
            continue
    
    # Filter products with total quantity < threshold
    low_performers = []
    for product_name, data in product_data.items():
        if data['total_quantity'] < threshold:
            low_performers.append((
                product_name,
                data['total_quantity'],
                round(data['total_revenue'], 2)
            ))
    
    # Sort by total quantity in ascending order
    low_performers.sort(key=lambda x: x[1])
    
    return low_performers


# ============================================
# Existing functions (keeping for compatibility)
# ============================================

def validate_and_filter(transactions: List[Dict], 
                       region: Optional[str] = None, 
                       min_amount: Optional[float] = None, 
                       max_amount: Optional[float] = None) -> Tuple[List[Dict], int, Dict[str, Any]]:
    """
    Validates transactions and applies optional filters

    Parameters:
    - transactions: list of transaction dictionaries
    - region: filter by specific region (optional)
    - min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
    - max_amount: maximum transaction amount (optional)

    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """
    
    print("=" * 60)
    print("DATA VALIDATION AND FILTERING")
    print("=" * 60)
    
    # Initialize counters and lists
    valid_transactions = []
    invalid_transactions = []
    filtered_transactions = transactions.copy()
    
    # Calculate transaction amounts for all transactions
    for transaction in filtered_transactions:
        try:
            amount = transaction['Quantity'] * transaction['UnitPrice']
            transaction['Amount'] = amount
        except KeyError:
            transaction['Amount'] = 0
    
    # Step 1: Display available options to user
    print("\nStep 1: Analyzing available data...")
    
    # Get unique regions
    regions = sorted(set(t.get('Region', '') for t in filtered_transactions if t.get('Region')))
    print(f"Available Regions: {', '.join(regions)}")
    
    # Get amount range
    amounts = [t.get('Amount', 0) for t in filtered_transactions]
    if amounts:
        min_available = min(amounts)
        max_available = max(amounts)
        print(f"Transaction Amount Range: ${min_available:,.2f} to ${max_available:,.2f}")
    
    # Step 2: Validate transactions
    print("\nStep 2: Validating transactions...")
    for transaction in transactions:
        is_valid = True
        error_messages = []
        
        # Check all required fields are present
        required_fields = ['TransactionID', 'Date', 'ProductID', 'ProductName', 
                          'Quantity', 'UnitPrice', 'CustomerID', 'Region']
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                is_valid = False
                error_messages.append(f"Missing {field}")
                break
        
        if is_valid:
            # Check TransactionID starts with 'T'
            if not str(transaction['TransactionID']).startswith('T'):
                is_valid = False
                error_messages.append("TransactionID must start with 'T'")
            
            # Check ProductID starts with 'P'
            if not str(transaction['ProductID']).startswith('P'):
                is_valid = False
                error_messages.append("ProductID must start with 'P'")
            
            # Check CustomerID starts with 'C'
            if not str(transaction['CustomerID']).startswith('C'):
                is_valid = False
                error_messages.append("CustomerID must start with 'C'")
            
            # Check Quantity > 0
            try:
                quantity = int(transaction['Quantity'])
                if quantity <= 0:
                    is_valid = False
                    error_messages.append(f"Quantity must be > 0 (got {quantity})")
            except (ValueError, TypeError):
                is_valid = False
                error_messages.append("Invalid Quantity value")
            
            # Check UnitPrice > 0
            try:
                unit_price = float(transaction['UnitPrice'])
                if unit_price <= 0:
                    is_valid = False
                    error_messages.append(f"UnitPrice must be > 0 (got {unit_price})")
            except (ValueError, TypeError):
                is_valid = False
                error_messages.append("Invalid UnitPrice value")
        
        if is_valid:
            valid_transactions.append(transaction)
        else:
            transaction['ValidationError'] = ', '.join(error_messages)
            invalid_transactions.append(transaction)
    
    print(f"Total input transactions: {len(transactions)}")
    print(f"Valid transactions: {len(valid_transactions)}")
    print(f"Invalid transactions: {len(invalid_transactions)}")
    
    # Step 3: Apply region filter (if specified)
    filtered_by_region = 0
    if region:
        print(f"\nStep 3: Applying region filter for '{region}'...")
        region_filtered = [t for t in valid_transactions if t.get('Region', '').lower() == region.lower()]
        filtered_by_region = len(valid_transactions) - len(region_filtered)
        valid_transactions = region_filtered
        print(f"Transactions after region filter: {len(valid_transactions)}")
    else:
        print("\nStep 3: No region filter applied")
    
    # Step 4: Apply amount filters (if specified)
    filtered_by_amount = 0
    if min_amount is not None or max_amount is not None:
        print(f"\nStep 4: Applying amount filters...")
        print(f"  - Minimum amount: {'$' + str(min_amount) if min_amount is not None else 'Not specified'}")
        print(f"  - Maximum amount: {'$' + str(max_amount) if max_amount is not None else 'Not specified'}")
        
        amount_filtered = []
        for transaction in valid_transactions:
            amount = transaction.get('Amount', 0)
            include = True
            
            if min_amount is not None and amount < min_amount:
                include = False
            
            if max_amount is not None and amount > max_amount:
                include = False
            
            if include:
                amount_filtered.append(transaction)
        
        filtered_by_amount = len(valid_transactions) - len(amount_filtered)
        valid_transactions = amount_filtered
        print(f"Transactions after amount filter: {len(valid_transactions)}")
    else:
        print("\nStep 4: No amount filters applied")
    
    # Calculate final summary
    filter_summary = {
        'total_input': len(transactions),
        'invalid': len(invalid_transactions),
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid_transactions),
        'available_regions': regions,
        'amount_range': {
            'min': min_available if amounts else 0,
            'max': max_available if amounts else 0
        }
    }
    
    # Display final summary
    print("\n" + "=" * 60)
    print("FILTERING SUMMARY")
    print("=" * 60)
    print(f"Total transactions processed: {filter_summary['total_input']}")
    print(f"Invalid transactions removed: {filter_summary['invalid']}")
    print(f"Filtered by region: {filter_summary['filtered_by_region']}")
    print(f"Filtered by amount: {filter_summary['filtered_by_amount']}")
    print(f"Final valid transactions: {filter_summary['final_count']}")
    
    return valid_transactions, len(invalid_transactions), filter_summary


class DataProcessor:
    """Processes and analyzes sales data"""
    
    @staticmethod
    def clean_product_name(product_name: str) -> str:
        """
        Clean product name by removing commas and extra spaces
        
        Args:
            product_name: Raw product name
            
        Returns:
            Cleaned product name
        """
        # Remove commas and replace with space
        cleaned = product_name.replace(',', ' ')
        # Remove extra spaces
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    @staticmethod
    def clean_numeric_value(value: str) -> Optional[float]:
        """
        Clean numeric values by removing commas and converting to float
        
        Args:
            value: String numeric value (may contain commas)
            
        Returns:
            Float value or None if invalid
        """
        try:
            # Remove commas and any non-numeric characters except decimal point
            cleaned = value.replace(',', '').strip()
            
            # Handle negative values
            if cleaned.startswith('-'):
                return None
            
            # Convert to float
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def validate_record(record: Dict) -> Tuple[bool, str]:
        """
        Validate a sales record against business rules
        
        Args:
            record: Sales record dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check TransactionID starts with 'T'
        if not record.get('TransactionID', '').startswith('T'):
            return False, "TransactionID must start with 'T'"
        
        # Check CustomerID is not empty
        if not record.get('CustomerID', '').strip():
            return False, "Missing CustomerID"
        
        # Check Region is not empty
        if not record.get('Region', '').strip():
            return False, "Missing Region"
        
        # Validate Quantity
        quantity = DataProcessor.clean_numeric_value(str(record.get('Quantity', '0')))
        if quantity is None or quantity <= 0:
            return False, f"Invalid Quantity: {record.get('Quantity')}"
        
        # Validate UnitPrice
        unit_price = DataProcessor.clean_numeric_value(str(record.get('UnitPrice', '0')))
        if unit_price is None or unit_price <= 0:
            return False, f"Invalid UnitPrice: {record.get('UnitPrice')}"
        
        # Validate Date format (YYYY-MM-DD)
        date_str = record.get('Date', '')
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return False, f"Invalid Date format: {date_str}"
        
        # Validate ProductID format (should start with 'P')
        product_id = record.get('ProductID', '')
        if not product_id.startswith('P'):
            return False, f"Invalid ProductID: {product_id}"
        
        return True, "Valid"
    
    @staticmethod
    def clean_and_validate_records(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Clean and validate all sales records
        
        Args:
            records: List of raw sales records
            
        Returns:
            Tuple of (valid_records, invalid_records)
        """
        valid_records = []
        invalid_records = []
        
        for record in records:
            if not record:
                continue
            
            # Clean the data
            cleaned_record = record.copy()
            
            # Clean ProductName
            cleaned_record['ProductName'] = DataProcessor.clean_product_name(
                cleaned_record.get('ProductName', '')
            )
            
            # Clean and convert numeric fields
            quantity = DataProcessor.clean_numeric_value(str(cleaned_record.get('Quantity', '0')))
            unit_price = DataProcessor.clean_numeric_value(str(cleaned_record.get('UnitPrice', '0')))
            
            cleaned_record['Quantity'] = quantity
            cleaned_record['UnitPrice'] = unit_price
            
            # Validate the cleaned record
            is_valid, error_msg = DataProcessor.validate_record(cleaned_record)
            
            if is_valid and quantity is not None and unit_price is not None:
                # Calculate total price
                cleaned_record['TotalPrice'] = quantity * unit_price
                valid_records.append(cleaned_record)
            else:
                cleaned_record['Error'] = error_msg
                invalid_records.append(cleaned_record)
        
        return valid_records, invalid_records
    
    @staticmethod
    def analyze_sales(valid_records: List[Dict]) -> Dict:
        """
        Perform sales analysis on valid records
        
        Args:
            valid_records: List of valid sales records
            
        Returns:
            Dictionary containing analysis results
        """
        if not valid_records:
            return {}
        
        analysis = {
            'summary': {},
            'by_region': {},
            'by_product': {},
            'top_customers': [],
            'sales_trends': {}
        }
        
        # Calculate summary statistics
        total_sales = sum(record.get('TotalPrice', 0) for record in valid_records)
        total_quantity = sum(record.get('Quantity', 0) for record in valid_records)
        avg_price = total_sales / total_quantity if total_quantity > 0 else 0
        
        analysis['summary'] = {
            'total_records': len(valid_records),
            'total_sales': round(total_sales, 2),
            'total_quantity': int(total_quantity),
            'average_unit_price': round(avg_price, 2),
            'unique_customers': len(set(r.get('CustomerID') for r in valid_records)),
            'unique_products': len(set(r.get('ProductID') for r in valid_records))
        }
        
        # Analyze by region
        region_sales = {}
        for record in valid_records:
            region = record.get('Region')
            total_price = record.get('TotalPrice', 0)
            
            if region not in region_sales:
                region_sales[region] = {
                    'total_sales': 0,
                    'total_quantity': 0,
                    'transactions': 0
                }
            
            region_sales[region]['total_sales'] += total_price
            region_sales[region]['total_quantity'] += record.get('Quantity', 0)
            region_sales[region]['transactions'] += 1
        
        analysis['by_region'] = region_sales
        
        # Analyze by product
        product_sales = {}
        for record in valid_records:
            product_id = record.get('ProductID')
            product_name = record.get('ProductName')
            
            if product_id not in product_sales:
                product_sales[product_id] = {
                    'product_name': product_name,
                    'total_sales': 0,
                    'total_quantity': 0,
                    'transactions': 0
                }
            
            product_sales[product_id]['total_sales'] += record.get('TotalPrice', 0)
            product_sales[product_id]['total_quantity'] += record.get('Quantity', 0)
            product_sales[product_id]['transactions'] += 1
        
        # Sort products by total sales
        sorted_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]['total_sales'],
            reverse=True
        )
        analysis['by_product'] = dict(sorted_products[:10])  # Top 10 products
        
        # Find top customers
        customer_sales = {}
        for record in valid_records:
            customer_id = record.get('CustomerID')
            
            if customer_id not in customer_sales:
                customer_sales[customer_id] = {
                    'total_spent': 0,
                    'transactions': 0
                }
            
            customer_sales[customer_id]['total_spent'] += record.get('TotalPrice', 0)
            customer_sales[customer_id]['transactions'] += 1
        
        # Sort customers by total spent
        sorted_customers = sorted(
            customer_sales.items(),
            key=lambda x: x[1]['total_spent'],
            reverse=True
        )
        analysis['top_customers'] = [
            {'customer_id': cust_id, **data} 
            for cust_id, data in sorted_customers[:10]
        ]
        
        # Analyze sales trends by date
        date_sales = {}
        for record in valid_records:
            date = record.get('Date')
            if date not in date_sales:
                date_sales[date] = 0
            date_sales[date] += record.get('TotalPrice', 0)
        
        # Sort dates chronologically
        sorted_dates = sorted(date_sales.items())
        analysis['sales_trends'] = dict(sorted_dates)
        
        return analysis
    
    @staticmethod
    def generate_sales_report(analysis: Dict) -> str:
        """
        Generate a formatted sales report string
        
        Args:
            analysis: Dictionary containing analysis results
            
        Returns:
            Formatted report string
        """
        if not analysis:
            return "No data available for analysis"
        
        report = []
        report.append("=" * 60)
        report.append("SALES ANALYSIS REPORT")
        report.append("=" * 60)
        
        # Summary Section
        summary = analysis.get('summary', {})
        report.append("\nSUMMARY STATISTICS:")
        report.append("-" * 40)
        report.append(f"Total Valid Records: {summary.get('total_records', 0)}")
        report.append(f"Total Sales: ${summary.get('total_sales', 0):,.2f}")
        report.append(f"Total Quantity Sold: {summary.get('total_quantity', 0):,}")
        report.append(f"Average Unit Price: ${summary.get('average_unit_price', 0):,.2f}")
        report.append(f"Unique Customers: {summary.get('unique_customers', 0)}")
        report.append(f"Unique Products: {summary.get('unique_products', 0)}")
        
        # Region Analysis
        report.append("\nREGION-WISE ANALYSIS:")
        report.append("-" * 40)
        for region, data in analysis.get('by_region', {}).items():
            report.append(f"{region}:")
            report.append(f"  Total Sales: ${data['total_sales']:,.2f}")
            report.append(f"  Quantity Sold: {data['total_quantity']:,}")
            report.append(f"  Transactions: {data['transactions']}")
        
        # Top Products
        report.append("\nTOP SELLING PRODUCTS:")
        report.append("-" * 40)
        for i, (product_id, data) in enumerate(analysis.get('by_product', {}).items(), 1):
            report.append(f"{i}. {product_id} - {data['product_name']}")
            report.append(f"   Sales: ${data['total_sales']:,.2f}")
            report.append(f"   Quantity: {data['total_quantity']:,}")
        
        # Top Customers
        report.append("\nTOP CUSTOMERS:")
        report.append("-" * 40)
        for i, customer in enumerate(analysis.get('top_customers', [])[:5], 1):
            report.append(f"{i}. Customer {customer['customer_id']}")
            report.append(f"   Total Spent: ${customer['total_spent']:,.2f}")
            report.append(f"   Transactions: {customer['transactions']}")
        
        return "\n".join(report)


# ============================================
"""
Test script for Tasks 2.1, 2.2, and 2.3
"""

import os
import sys
from utils.file_handler import read_sales_data, parse_transactions
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)

def test_part_2_functions():
    """Test all Part 2 functions"""
    
    print("=" * 70)
    print("TESTING PART 2: DATA PROCESSING FUNCTIONS")
    print("=" * 70)
    
    # Read and parse test data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "data", "sales_data.txt")
    
    print("\nLoading test data...")
    lines = read_sales_data(data_file)
    transactions = parse_transactions(lines)
    
    if not transactions:
        print("Error: No transactions to test")
        return
    
    print(f"\nLoaded {len(transactions)} transactions for testing")
    
    total_points = 0
    criteria_results = []
    
    # ============================================
    # Task 2.1: Sales Summary Calculator
    # ============================================
    print("\n" + "=" * 70)
    print("TASK 2.1: SALES SUMMARY CALCULATOR")
    print("=" * 70)
    
    # (a) Calculate Total Revenue
    print("\n(a) Testing calculate_total_revenue()...")
    total_revenue = calculate_total_revenue(transactions)
    print(f"Total Revenue: ${total_revenue:,.2f}")
    
    # Calculate expected total from sample data
    expected_revenue = 0
    for trans in transactions:
        expected_revenue += trans['Quantity'] * trans['UnitPrice']
    
    if abs(total_revenue - expected_revenue) < 0.01:
        criteria_results.append("✓ calculate_total_revenue(): Returns exact correct total (+3 points)")
        total_points += 3
    else:
        criteria_results.append(f"✗ calculate_total_revenue(): Expected ${expected_revenue:,.2f}, got ${total_revenue:,.2f}")
    
    # (b) Region-wise Sales Analysis
    print("\n(b) Testing region_wise_sales()...")
    region_sales = region_wise_sales(transactions)
    print(f"Regions found: {list(region_sales.keys())}")
    
    # Validate region data
    region_tests_passed = 0
    if region_sales:
        # Test 1: Check totals per region
        region_totals_correct = True
        for region, data in region_sales.items():
            print(f"  {region}: ${data['total_sales']:,.2f} ({data['transaction_count']} transactions)")
        
        # Test 2: Check transaction counts
        total_transactions = sum(data['transaction_count'] for data in region_sales.values())
        if total_transactions == len(transactions):
            region_tests_passed += 1
        
        # Test 3: Check percentages sum to ~100%
        total_percentage = sum(data['percentage'] for data in region_sales.values())
        if 99.9 <= total_percentage <= 100.1:
            region_tests_passed += 1
        
        if region_tests_passed == 3:
            criteria_results.append("✓ region_wise_sales(): All region calculations correct (+4 points)")
            total_points += 4
        else:
            criteria_results.append(f"✗ region_wise_sales(): {region_tests_passed}/3 tests passed")
    
    # (c) Top Selling Products
    print("\n(c) Testing top_selling_products()...")
    top_products = top_selling_products(transactions, n=5)
    print(f"Top 5 products by quantity sold:")
    for i, (name, qty, revenue) in enumerate(top_products, 1):
        print(f"  {i}. {name}: {qty} units, ${revenue:,.2f}")
    
    # Validate top products
    if len(top_products) == 5:
        # Check sorting (should be descending by quantity)
        sorted_correctly = all(
            top_products[i][1] >= top_products[i+1][1] 
            for i in range(len(top_products)-1)
        )
        
        if sorted_correctly:
            criteria_results.append("✓ top_selling_products(): Correct aggregation and sorting (+4 points)")
            total_points += 4
        else:
            criteria_results.append("
