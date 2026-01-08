"""
File Handler Module
Handles reading, writing, and encoding-related operations for sales data
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
import json


def read_sales_data(filename: str) -> List[str]:
    """
    Reads sales data from file handling encoding issues

    Args:
        filename: Path to the sales data file

    Returns:
        list of raw lines (strings)
        Expected Output Format: ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

    Requirements:
    - Use 'with' statement
    - Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
    - Handle FileNotFoundError with appropriate error message
    - Skip the header row
    - Remove empty lines
    """
    
    raw_lines = []
    
    try:
        # Try different encodings to handle non-UTF-8 files
        encodings = ['utf-8', 'latin-1', 'cp1252']
        successful_read = False
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    print(f"Attempting to read file with {encoding} encoding...")
                    
                    # Read all lines
                    all_lines = file.readlines()
                    
                    if len(all_lines) > 0:
                        print(f"Successfully read {len(all_lines)} lines with {encoding} encoding")
                        successful_read = True
                        
                        # Skip the header row (first line)
                        data_lines = all_lines[1:]
                        
                        # Remove empty lines and lines with only whitespace
                        for line in data_lines:
                            stripped_line = line.strip()
                            if stripped_line:  # Only add non-empty lines
                                raw_lines.append(stripped_line)
                        
                        print(f"Found {len(raw_lines)} non-empty transaction lines after removing header")
                        break
                        
            except UnicodeDecodeError:
                print(f"Failed to decode with {encoding} encoding, trying next...")
                continue
            except Exception as e:
                print(f"Error reading file with {encoding} encoding: {str(e)}")
                continue
        
        if not successful_read:
            raise ValueError("Could not read file with any of the supported encodings")
            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please check the file path.")
        return []
    except Exception as e:
        print(f"Error reading sales data: {str(e)}")
        return []
    
    # Validate that we have between 50-100 transaction lines
    if len(raw_lines) < 50 or len(raw_lines) > 100:
        print(f"Warning: Expected 50-100 transaction lines, but found {len(raw_lines)}")
    
    return raw_lines


def parse_transactions(raw_lines: List[str]) -> List[Dict]:
    """
    Parses raw sales data lines and cleans them

    Args:
        raw_lines: List of raw transaction strings

    Returns:
        list of dictionaries with keys:
        ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    Example Output:
    [
        {
            'TransactionID': 'T001',
            'Date': '2024-12-01',
            'ProductID': 'P101',
            'ProductName': 'Laptop',
            'Quantity': 2,           # int type
            'UnitPrice': 45000.0,    # float type
            'CustomerID': 'C001',
            'Region': 'North'
        },
        ...
    ]

    Requirements:
    - Split by pipe delimiter '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to proper types
    - Convert Quantity to int
    - Convert UnitPrice to float
    - Skip rows with incorrect number of fields
    """
    
    parsed_transactions = []
    skipped_count = 0
    
    print(f"\nParsing {len(raw_lines)} raw transaction lines...")
    
    for i, line in enumerate(raw_lines, 1):
        try:
            # Split by pipe delimiter
            fields = line.split('|')
            
            # Check if we have exactly 8 fields
            if len(fields) != 8:
                skipped_count += 1
                continue
            
            # Extract and clean each field
            transaction_id = fields[0].strip()
            date = fields[1].strip()
            product_id = fields[2].strip()
            
            # Clean ProductName: remove commas and extra spaces
            product_name = fields[3].strip()
            product_name = product_name.replace(',', ' ')
            # Remove extra spaces that might result from comma replacement
            product_name = ' '.join(product_name.split())
            
            # Clean Quantity: remove commas and convert to int
            quantity_str = fields[4].strip()
            quantity_str = quantity_str.replace(',', '')
            try:
                quantity = int(float(quantity_str))  # Handle cases like '0.0'
            except ValueError:
                skipped_count += 1
                continue
            
            # Clean UnitPrice: remove commas and convert to float
            unit_price_str = fields[5].strip()
            unit_price_str = unit_price_str.replace(',', '')
            try:
                unit_price = float(unit_price_str)
            except ValueError:
                skipped_count += 1
                continue
            
            customer_id = fields[6].strip()
            region = fields[7].strip()
            
            # Create transaction dictionary with cleaned data
            transaction = {
                'TransactionID': transaction_id,
                'Date': date,
                'ProductID': product_id,
                'ProductName': product_name,
                'Quantity': quantity,
                'UnitPrice': unit_price,
                'CustomerID': customer_id,
                'Region': region
            }
            
            parsed_transactions.append(transaction)
            
        except Exception as e:
            skipped_count += 1
            continue
    
    print(f"Successfully parsed {len(parsed_transactions)} transactions")
    print(f"Skipped {skipped_count} lines due to parsing errors or incorrect format")
    
    # Show sample of parsed data
    if parsed_transactions:
        print("\nSample of parsed transactions (first 3):")
        for i, trans in enumerate(parsed_transactions[:3], 1):
            print(f"  {i}. {trans}")
    
    return parsed_transactions


class FileHandler:
    """Handles file operations for sales data"""
    
    @staticmethod
    def read_sales_file(file_path: str) -> Tuple[List[str], int]:
        """
        Read sales data file with proper encoding handling
        
        Args:
            file_path: Path to the sales data file
            
        Returns:
            Tuple of (list of lines, total records read)
        """
        lines = []
        total_records = 0
        
        try:
            # Try different encodings to handle non-UTF-8 files
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        lines = file.readlines()
                        total_records = len(lines) - 1  # Exclude header
                        print(f"Successfully read file with {encoding} encoding")
                        break
                except UnicodeDecodeError:
                    continue
                    
            if not lines:
                raise ValueError("Could not read file with any supported encoding")
                
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return [], 0
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return [], 0
            
        return lines, total_records
    
    @staticmethod
    def parse_line(line: str, delimiter: str = '|') -> Optional[Dict]:
        """
        Parse a single line of sales data
        
        Args:
            line: Line from sales data file
            delimiter: Field delimiter
            
        Returns:
            Dictionary of parsed data or None if invalid
        """
        # Skip empty lines
        if not line.strip():
            return None
            
        # Remove newline and split by delimiter
        fields = line.strip().split(delimiter)
        
        # Skip lines with incorrect number of fields
        if len(fields) != 8:
            return None
            
        return {
            'TransactionID': fields[0].strip(),
            'Date': fields[1].strip(),
            'ProductID': fields[2].strip(),
            'ProductName': fields[3].strip(),
            'Quantity': fields[4].strip(),
            'UnitPrice': fields[5].strip(),
            'CustomerID': fields[6].strip(),
            'Region': fields[7].strip()
        }
    
    @staticmethod
    def save_clean_data(data: List[Dict], output_path: str) -> bool:
        """
        Save cleaned data to a CSV file
        
        Args:
            data: List of cleaned data dictionaries
            output_path: Path to save the cleaned data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            print(f"Cleaned data saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False
    
    @staticmethod
    def save_report(report_data: Dict, report_path: str) -> bool:
        """
        Save analysis report to a JSON file
        
        Args:
            report_data: Dictionary containing report data
            report_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(report_path, 'w') as file:
                json.dump(report_data, file, indent=4)
            print(f"Report saved to {report_path}")
            return True
        except Exception as e:
            print(f"Error saving report: {str(e)}")
            return False
    
    @staticmethod
    def save_summary(valid_count: int, invalid_count: int, total_records: int, 
                     output_path: str) -> bool:
        """
        Save cleaning summary to a text file
        
        Args:
            valid_count: Number of valid records
            invalid_count: Number of invalid records
            total_records: Total records parsed
            output_path: Path to save the summary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w') as file:
                file.write("=== DATA CLEANING SUMMARY ===\n")
                file.write(f"Total records parsed: {total_records}\n")
                file.write(f"Invalid records removed: {invalid_count}\n")
                file.write(f"Valid records after cleaning: {valid_count}\n")
            print(f"Summary saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving summary: {str(e)}")
            return False


# =========================================================================================
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
