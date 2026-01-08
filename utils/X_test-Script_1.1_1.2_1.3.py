"""
Test script for Tasks 1.1, 1.2, and 1.3
"""

import os
import sys
from utils.file_handler import read_sales_data, parse_transactions
from utils.data_processor import validate_and_filter

def run_tests():
    """Run all tests for Tasks 1.1, 1.2, and 1.3"""
    
    print("=" * 70)
    print("TESTING TASKS 1.1, 1.2, AND 1.3")
    print("=" * 70)
    
    # Get the path to the sales data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "data", "sales_data.txt")
    
    # ============================================
    # Task 1.1: Read Sales Data with Encoding Handling
    # ============================================
    print("\n" + "=" * 70)
    print("TASK 1.1: Read Sales Data with Encoding Handling")
    print("=" * 70)
    
    points_1_1 = 0
    criteria_1_1 = []
    
    # Test 1.1.1: Read the file
    print("\n1. Testing file reading...")
    lines = read_sales_data(data_file)
    
    # Check if we got data
    if lines:
        criteria_1_1.append("✓ Successfully reads non-UTF-8 encoded file (+5 points)")
        points_1_1 += 5
    else:
        criteria_1_1.append("✗ Failed to read file (0 points)")
    
    # Check number of lines
    line_count = len(lines)
    if 50 <= line_count <= 100:
        criteria_1_1.append(f"✓ Returns list with {line_count} transaction lines (50-100 range) (+3 points)")
        points_1_1 += 3
    else:
        criteria_1_1.append(f"✗ Returns {line_count} lines, not 50-100 (0 points)")
    
    # Test with non-existent file
    print("\n2. Testing error handling...")
    non_existent = os.path.join(current_dir, "data", "non_existent.txt")
    result = read_sales_data(non_existent)
    if result == []:
        criteria_1_1.append("✓ Proper error handling for FileNotFoundError (+2 points)")
        points_1_1 += 2
    else:
        criteria_1_1.append("✗ No proper error handling for FileNotFoundError (0 points)")
    
    # ============================================
    # Task 1.2: Parse and Clean Data
    # ============================================
    print("\n" + "=" * 70)
    print("TASK 1.2: Parse and Clean Data")
    print("=" * 70)
    
    points_1_2 = 0
    criteria_1_2 = []
    
    # Parse the transactions
    print("\n1. Parsing transactions...")
    transactions = parse_transactions(lines)
    
    # Check if we parsed transactions
    if transactions and len(transactions) > 0:
        criteria_1_2.append("✓ Correctly parses all valid transactions (+5 points)")
        points_1_2 += 5
    else:
        criteria_1_2.append("✗ Failed to parse transactions (0 points)")
    
    # Check data types
    print("\n2. Checking data types...")
    type_errors = []
    for i, trans in enumerate(transactions[:10]):  # Check first 10
        if not isinstance(trans.get('Quantity', None), int):
            type_errors.append(f"Transaction {i}: Quantity is {type(trans.get('Quantity'))}, expected int")
        if not isinstance(trans.get('UnitPrice', None), (int, float)):
            type_errors.append(f"Transaction {i}: UnitPrice is {type(trans.get('UnitPrice'))}, expected float")
    
    if not type_errors:
        criteria_1_2.append("✓ Correct data types (Quantity as int, UnitPrice as float) (+4 points)")
        points_1_2 += 4
    else:
        criteria_1_2.append("✗ Incorrect data types (0 points)")
        for error in type_errors[:3]:  # Show first 3 errors
            print(f"  - {error}")
    
    # Check for commas in numeric fields
    print("\n3. Checking comma handling in numeric fields...")
    comma_issues = []
    for trans in transactions:
        # Check if original lines had commas that were removed
        for line in lines:
            if trans['TransactionID'] in line:
                if ',' in line and ('Quantity' in line or 'UnitPrice' in line):
                    # Check if parsing removed the comma
                    if isinstance(trans['Quantity'], int) and isinstance(trans['UnitPrice'], (int, float)):
                        pass  # Comma was properly handled
                    else:
                        comma_issues.append(f"Transaction {trans['TransactionID']}: Comma not properly handled")
                break
    
    if not comma_issues:
        criteria_1_2.append("✓ Handles commas in numeric fields (1,500 → 1500) (+3 points)")
        points_1_2 += 3
    else:
        criteria_1_2.append("✗ Does not handle commas in numeric fields (0 points)")
    
    # Check for commas in ProductName
    print("\n4. Checking comma handling in ProductName...")
    product_name_issues = []
    for trans in transactions:
        if ',' in trans.get('ProductName', ''):
            product_name_issues.append(f"Transaction {trans['TransactionID']}: Comma still in ProductName")
    
    if not product_name_issues:
        criteria_1_2.append("✓ Handles commas in ProductName field (+3 points)")
        points_1_2 += 3
    else:
        criteria_1_2.append("✗ Does not handle commas in ProductName (0 points)")
        for issue in product_name_issues[:3]:
            print(f"  - {issue}")
    
    # ============================================
    # Task 1.3: Data Validation and Filtering
    # ============================================
    print("\n" + "=" * 70)
    print("TASK 1.3: Data Validation and Filtering")
    print("=" * 70)
    
    points_1_3 = 0
    criteria_1_3 = []
    
    # Test validation and filtering
    print("\n1. Testing validation and
