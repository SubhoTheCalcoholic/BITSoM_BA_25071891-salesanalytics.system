"""
Data Processor Module
Handles data cleaning, validation, and analysis operations
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime


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

    Expected Output Format:
    (
        [list of valid filtered transactions],
        5,  # count of invalid transactions
        {
            'total_input': 100,
            'invalid': 5,
            'filtered_by_region': 20,
            'filtered_by_amount': 10,
            'final_count': 65
        }
    )

    Validation Rules:
    - Quantity must be > 0
    - UnitPrice must be > 0
    - All required fields must be present
    - TransactionID must start with 'T'
    - ProductID must start with 'P'
    - CustomerID must start with 'C'

    Filter Display:
    - Print available regions to user before filtering
    - Print transaction amount range (min/max) to user
    - Show count of records after each filter applied
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
