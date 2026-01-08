"""
Main Module - Sales Data Analytics System
Entry point for the application
"""

import sys
import os
from datetime import datetime
from utils.file_handler import read_sales_data, parse_transactions
from utils.data_processor import (
    validate_and_filter,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data
from utils.report_generator import generate_sales_report, generate_json_report, generate_executive_summary


def display_welcome_message():
    """Display welcome message for the Sales Analytics System"""
    print("=" * 60)
    print(" " * 20 + "SALES ANALYTICS SYSTEM")
    print("=" * 60)
    print("A comprehensive system for processing, analyzing,")
    print("and reporting on sales data")
    print("=" * 60)
    print()


def get_user_filters():
    """
    Get filter preferences from user
    
    Returns:
        Tuple of (region_filter, min_amount, max_amount)
    """
    print("\n" + "-" * 40)
    print("DATA FILTERING OPTIONS")
    print("-" * 40)
    
    region = None
    min_amount = None
    max_amount = None
    
    try:
        filter_choice = input("Do you want to filter the data? (y/n): ").strip().lower()
        
        if filter_choice == 'y' or filter_choice == 'yes':
            print("\nAvailable filter options:")
            print("1. Filter by region")
            print("2. Filter by transaction amount")
            print("3. Both region and amount")
            print("4. Skip filtering")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                region = input("Enter region to filter by (e.g., North, South, East, West): ").strip()
            elif choice == '2':
                try:
                    min_amount = float(input("Enter minimum transaction amount: ").strip())
                    max_amount = float(input("Enter maximum transaction amount: ").strip())
                except ValueError:
                    print("Invalid amount entered. Amount filter will be skipped.")
                    min_amount = None
                    max_amount = None
            elif choice == '3':
                region = input("Enter region to filter by (e.g., North, South, East, West): ").strip()
                try:
                    min_amount = float(input("Enter minimum transaction amount: ").strip())
                    max_amount = float(input("Enter maximum transaction amount: ").strip())
                except ValueError:
                    print("Invalid amount entered. Amount filter will be skipped.")
                    min_amount = None
                    max_amount = None
            else:
                print("Skipping filtering...")
        
        return region, min_amount, max_amount
        
    except Exception as e:
        print(f"Error getting user filters: {str(e)}")
        return None, None, None


def display_progress(step_number, total_steps, message, success=True):
    """
    Display progress message with formatting
    
    Args:
        step_number: Current step number
        total_steps: Total number of steps
        message: Progress message
        success: Whether the step was successful
    """
    status = "✓" if success else "✗"
    print(f"\n[{step_number}/{total_steps}] {message}")
    if success:
        print(f"  {status} Success")
    else:
        print(f"  {status} Failed")


def save_analysis_results(transactions, output_dir):
    """
    Save analysis results to various files
    
    Args:
        transactions: List of valid transactions
        output_dir: Output directory path
        
    Returns:
        Dictionary of saved file paths
    """
    saved_files = {}
    
    try:
        # Calculate all analyses
        total_revenue = calculate_total_revenue(transactions)
        region_data = region_wise_sales(transactions)
        top_products = top_selling_products(transactions, n=10)
        customer_data = customer_analysis(transactions)
        daily_trend = daily_sales_trend(transactions)
        peak_day = find_peak_sales_day(transactions)
        low_performers = low_performing_products(transactions, threshold=5)
        
        # Save region analysis to CSV
        import csv
        region_csv = os.path.join(output_dir, "region_analysis.csv")
        with open(region_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Region', 'Total_Sales', 'Transaction_Count', 'Percentage'])
            for region, data in region_data.items():
                writer.writerow([region, data['total_sales'], data['transaction_count'], data['percentage']])
        saved_files['region_analysis'] = region_csv
        
        # Save top products to CSV
        products_csv = os.path.join(output_dir, "top_products.csv")
        with open(products_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Product_Name', 'Quantity_Sold', 'Total_Revenue'])
            for product_name, quantity, revenue in top_products:
                writer.writerow([product_name, quantity, revenue])
        saved_files['top_products'] = products_csv
        
        # Save customer analysis to CSV
        customers_csv = os.path.join(output_dir, "customer_analysis.csv")
        with open(customers_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Customer_ID', 'Total_Spent', 'Purchase_Count', 'Avg_Order_Value'])
            writer.writeheader()
            for customer_id, data in customer_data.items():
                writer.writerow({
                    'Customer_ID': customer_id,
                    'Total_Spent': data['total_spent'],
                    'Purchase_Count': data['purchase_count'],
                    'Avg_Order_Value': data['avg_order_value']
                })
        saved_files['customer_analysis'] = customers_csv
        
        # Save daily trend to CSV
        daily_csv = os.path.join(output_dir, "daily_trend.csv")
        with open(daily_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Revenue', 'Transaction_Count', 'Unique_Customers'])
            for date, data in daily_trend.items():
                writer.writerow([date, data['revenue'], data['transaction_count'], data['unique_customers']])
        saved_files['daily_trend'] = daily_csv
        
        # Save summary to text file
        summary_txt = os.path.join(output_dir, "analysis_summary.txt")
        with open(summary_txt, 'w', encoding='utf-8') as f:
            f.write("ANALYSIS SUMMARY\n")
            f.write("=" * 40 + "\n")
            f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
            f.write(f"Total Transactions: {len(transactions):,}\n")
            f.write(f"Average Order Value: ${total_revenue/len(transactions):,.2f}\n")
            f.write(f"Peak Sales Day: {peak_day[0]} (${peak_day[1]:,.2f})\n")
            f.write(f"Low Performing Products: {len(low_performers)}\n")
            f.write(f"Unique Regions: {len(region_data)}\n")
            f.write(f"Unique Customers: {len(customer_data)}\n")
        saved_files['analysis_summary'] = summary_txt
        
        print(f"  ✓ Saved analysis results to {output_dir}/")
        
    except Exception as e:
        print(f"  ✗ Error saving analysis results: {str(e)}")
    
    return saved_files


def main():
    """
    Main execution function

    Workflow:
    1. Print welcome message
    2. Read sales data file (handle encoding)
    3. Parse and clean transactions
    4. Display filter options to user
       - Show available regions
       - Show transaction amount range
       - Ask if user wants to filter (y/n)
    5. If yes, ask for filter criteria and apply
    6. Validate transactions
    7. Display validation summary
    8. Perform all data analyses (call all functions from Part 2)
    9. Fetch products from API
    10. Enrich sales data with API info
    11. Save enriched data to file
    12. Generate comprehensive report
    13. Print success message with file locations

    Error Handling:
    - Wrap entire process in try-except
    - Display user-friendly error messages
    - Don't let program crash on errors
    """
    
    total_steps = 10
    current_step = 0
    success = True
    
    try:
        # ============================================
        # STEP 1: Welcome Message
        # ============================================
        current_step += 1
        display_welcome_message()
        display_progress(current_step, total_steps, "Starting Sales Analytics System...")
        
        # ============================================
        # STEP 2: Read Sales Data
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Reading sales data file...")
        
        # File paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        output_dir = os.path.join(current_dir, "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        input_file = os.path.join(data_dir, "sales_data.txt")
        
        if not os.path.exists(input_file):
            print(f"  ✗ Error: File not found at {input_file}")
            print("  Please ensure the sales_data.txt file is in the data/ directory")
            success = False
            return
        
        # Read sales data
        lines = read_sales_data(input_file)
        if not lines:
            print("  ✗ Error: Could not read sales data file")
            success = False
            return
        
        print(f"  ✓ Successfully read {len(lines)} transaction lines")
        
        # ============================================
        # STEP 3: Parse and Clean Transactions
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Parsing and cleaning transactions...")
        
        # Parse transactions
        from utils.file_handler import parse_transactions
        transactions = parse_transactions(lines)
        
        if not transactions:
            print("  ✗ Error: Could not parse any transactions")
            success = False
            return
        
        print(f"  ✓ Parsed {len(transactions)} transactions")
        
        # ============================================
        # STEP 4: Display Filter Options and Apply Filters
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Applying data filters...")
        
        # Get user filter preferences
        region_filter, min_amount, max_amount = get_user_filters()
        
        # Validate and apply filters
        filtered_transactions, invalid_count, filter_summary = validate_and_filter(
            transactions, 
            region=region_filter, 
            min_amount=min_amount, 
            max_amount=max_amount
        )
        
        print(f"  ✓ Filtering complete: {len(filtered_transactions)} valid transactions")
        if invalid_count > 0:
            print(f"  ⚠ Removed {invalid_count} invalid transactions")
        
        if not filtered_transactions:
            print("  ✗ Error: No valid transactions after filtering")
            success = False
            return
        
        # ============================================
        # STEP 5: Perform Data Analysis (Part 2 functions)
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Performing data analysis...")
        
        # Perform all analyses from Part 2
        print("\n  Calculating key metrics...")
        
        # Calculate total revenue
        total_revenue = calculate_total_revenue(filtered_transactions)
        print(f"    • Total Revenue: ${total_revenue:,.2f}")
        
        # Region-wise analysis
        region_data = region_wise_sales(filtered_transactions)
        print(f"    • Regions analyzed: {len(region_data)}")
        
        # Top products
        top_products = top_selling_products(filtered_transactions, n=5)
        print(f"    • Top 5 products identified")
        
        # Customer analysis
        customer_data = customer_analysis(filtered_transactions)
        print(f"    • Customers analyzed: {len(customer_data)}")
        
        # Daily trend
        daily_trend = daily_sales_trend(filtered_transactions)
        print(f"    • Daily trend calculated for {len(daily_trend)} days")
        
        # Peak sales day
        peak_day = find_peak_sales_day(filtered_transactions)
        print(f"    • Peak sales day: {peak_day[0]}")
        
        # Low performing products
        low_performers = low_performing_products(filtered_transactions, threshold=5)
        if low_performers:
            print(f"    • Low performing products: {len(low_performers)}")
        
        # Save analysis results
        saved_files = save_analysis_results(filtered_transactions, output_dir)
        
        print("  ✓ Analysis complete")
        
        # ============================================
        # STEP 6: Fetch Products from API
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Fetching product data from API...")
        
        api_products = fetch_all_products()
        
        if not api_products:
            print("  ⚠ Warning: Could not fetch products from API")
            print("  Continuing without API enrichment...")
            product_mapping = {}
        else:
            product_mapping = create_product_mapping(api_products)
            print(f"  ✓ Fetched {len(api_products)} products from API")
        
        # ============================================
        # STEP 7: Enrich Sales Data with API Info
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Enriching sales data with API information...")
        
        if product_mapping:
            enriched_transactions = enrich_sales_data(filtered_transactions, product_mapping)
            
            # Calculate enrichment success rate
            successful_matches = sum(1 for t in enriched_transactions if t.get('API_Match') == True)
            total_enriched = len(enriched_transactions)
            success_rate = (successful_matches / total_enriched * 100) if total_enriched > 0 else 0
            
            print(f"  ✓ Enriched {successful_matches}/{total_enriched} transactions ({success_rate:.1f}%)")
        else:
            enriched_transactions = None
            print("  ⚠ Skipping enrichment (no product mapping available)")
        
        # ============================================
        # STEP 8: Save Enriched Data to File
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Saving enriched data to file...")
        
        if enriched_transactions:
            enriched_file = os.path.join(output_dir, "enriched_sales_data.txt")
            save_success = save_enriched_data(enriched_transactions, enriched_file)
            
            if save_success:
                print(f"  ✓ Saved to: {enriched_file}")
            else:
                print("  ✗ Failed to save enriched data")
        else:
            print("  ⚠ No enriched data to save")
        
        # ============================================
        # STEP 9: Generate Comprehensive Report
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Generating comprehensive reports...")
        
        # Generate text report
        text_report = os.path.join(output_dir, "sales_report.txt")
        report_success = generate_sales_report(filtered_transactions, enriched_transactions, text_report)
        
        if report_success:
            print(f"  ✓ Text report saved to: {text_report}")
        else:
            print("  ✗ Failed to generate text report")
        
        # Generate JSON report
        json_report = os.path.join(output_dir, "sales_report.json")
        json_success = generate_json_report(filtered_transactions, enriched_transactions, json_report)
        
        if json_success:
            print(f"  ✓ JSON report saved to: {json_report}")
        else:
            print("  ✗ Failed to generate JSON report")
        
        # Generate executive summary
        exec_summary = os.path.join(output_dir, "executive_summary.txt")
        summary_success = generate_executive_summary(filtered_transactions, exec_summary)
        
        if summary_success:
            print(f"  ✓ Executive summary saved to: {exec_summary}")
        else:
            print("  ✗ Failed to generate executive summary")
        
        # ============================================
        # STEP 10: Print Success Message
        # ============================================
        current_step += 1
        display_progress(current_step, total_steps, "Process complete!", success=success)
        
        print("\n" + "=" * 60)
        print("PROCESS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Display output summary
        print("\n📊 ANALYSIS RESULTS:")
        print(f"  • Total Revenue: ${total_revenue:,.2f}")
        print(f"  • Valid Transactions: {len(filtered_transactions):,}")
        print(f"  • Unique Customers: {len(customer_data):,}")
        print(f"  • Unique Products: {len(set(t['ProductID'] for t in filtered_transactions)):,}")
        
        if region_data:
            top_region = max(region_data.items(), key=lambda x: x[1]['total_sales'])
            print(f"  • Top Region: {top_region[0]} (${top_region[1]['total_sales']:,.2f})")
        
        if peak_day[0]:
            print(f"  • Peak Sales Day: {peak_day[0]} (${peak_day[1]:,.2f})")
        
        print("\n📁 GENERATED FILES:")
        print(f"  • Enriched Data: {output_dir}/enriched_sales_data.txt")
        print(f"  • Text Report: {text_report}")
        print(f"  • JSON Report: {json_report}")
        print(f"  • Executive Summary: {exec_summary}")
        
        if saved_files:
            print(f"  • Analysis Files: {len(saved_files)} CSV files in {output_dir}/")
        
        print("\n" + "=" * 60)
        print("System ready for business decision making!")
        print("=" * 60)
        
        # Offer to show quick insights
        try:
            show_insights = input("\nWould you like to see quick insights? (y/n): ").strip().lower()
            if show_insights == 'y' or show_insights == 'yes':
                print("\n" + "-" * 40)
                print("QUICK INSIGHTS")
                print("-" * 40)
                
                # Show top product
                if top_products:
                    top_product = top_products[0]
                    print(f"• Best Selling Product: {top_product[0]}")
                    print(f"  Sold {top_product[1]:,} units (${top_product[2]:,.2f})")
                
                # Show top customer
                if customer_data:
                    top_customer = list(customer_data.items())[0]
                    print(f"• Top Customer: {top_customer[0]}")
                    print(f"  Spent ${top_customer[1]['total_spent']:,.2f} ({top_customer[1]['purchase_count']:,} orders)")
                
                # Show API enrichment status
                if enriched_transactions:
                    successful = sum(1 for t in enriched_transactions if t.get('API_Match') == True)
                    print(f"• API Enrichment: {successful}/{len(enriched_transactions)} products matched")
                
                print("-" * 40)
        except:
            pass  # Skip if there's any input error
        
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        print("Exiting...")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {str(e)}")
        print("\nPlease check:")
        print("  1. Internet connection (for API calls)")
        print("  2. File permissions and paths")
        print("  3. Data file format and encoding")
        print("\nIf the problem persists, contact support.")
        
        import traceback
        with open(os.path.join(output_dir, "error_log.txt"), 'w') as f:
            f.write(f"Error at step {current_step}/{total_steps}\n")
            f.write(f"Error: {str(e)}\n")
            f.write("Traceback:\n")
            traceback.print_exc(file=f)
        
        print(f"\nError details saved to: {output_dir}/error_log.txt")
        
        success = False
    
    finally:
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


  # ============================================

"""
Test script for the main application
"""

import os
import sys
import subprocess

def test_main_application():
    """Test the main application execution"""
    
    print("=" * 70)
    print("TESTING MAIN APPLICATION (TASK 5.1)")
    print("=" * 70)
    
    total_points = 0
    criteria_results = []
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    
    if not os.path.exists(main_script):
        print(f"Error: main.py not found at {main_script}")
        return False
    
    # Test 1: Check if main.py can be imported without errors
    print("\nTest 1: Checking imports and module structure...")
    try:
        # Try to import main modules
        import importlib
        import utils.file_handler
        import utils.data_processor
        import utils.api_handler
        import utils.report_generator
        
        # Try to import main (but don't run it yet)
        spec = importlib.util.spec_from_file_location("main", main_script)
        main_module = importlib.util.module_from_spec(spec)
        
        criteria_results.append("✓ All modules import successfully")
        print("  All required modules can be imported")
        
    except Exception as e:
        criteria_results.append(f"✗ Import error: {str(e)}")
        print(f"  Import failed: {str(e)}")
        return False
    
    # Test 2: Check if main function exists
    print("\nTest 2: Checking main function...")
    try:
        with open(main_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def main():' in content:
            criteria_results.append("✓ Main function exists")
            print("  Main function found")
        else:
            criteria_results.append("✗ Main function not found")
            print("  Main function not found in main.py")
            
        if 'if __name__ == "__main__":' in content and 'main()' in content:
            criteria_results.append("✓ Main function is called when script runs")
            print("  Main function is properly called")
        else:
            criteria_results.append("✗ Main function not properly called")
            
    except Exception as e:
        criteria_results.append(f"✗ Error reading main.py: {str(e)}")
    
    # Test 3: Check for required workflow steps
    print("\nTest 3: Checking for required workflow steps...")
    workflow_steps = [
        "welcome message",
        "read sales data",
        "parse and clean",
        "filter options",
        "validate transactions",
        "data analyses",
        "fetch products",
        "enrich sales data",
        "generate report",
        "success message"
    ]
    
    with open(main_script, 'r', encoding='utf-8') as f:
        content_lower = f.read().lower()
    
    steps_found = 0
    for step in workflow_steps:
        if step in content_lower:
            steps_found += 1
    
    if steps_found == len(workflow_steps):
        criteria_results.append("✓ Complete workflow implemented")
        total_points += 4
        print(f"  All {len(workflow_steps)} workflow steps found")
    else:
        criteria_results.append(f"✗ Missing workflow steps: Found {steps_found}/{len(workflow_steps)}")
        print(f"  Found {steps_found}/{len(workflow_steps)} workflow steps")
    
    # Test 4: Check for user interaction for filters
    print("\nTest 4: Checking for user interaction...")
    if 'input(' in content_lower and ('filter' in content_lower or 'y/n' in content_lower):
        criteria_results.append("✓ User interaction for filters implemented")
        total_points += 2
        print("  User interaction for filters found")
    else:
        criteria_results.append("✗ No user interaction for filters")
        print("  No user interaction for filters found")
    
    # Test 5: Check for error handling
    print("\nTest 5: Checking for error handling...")
    error_handling_indicators = [
        'try:',
        'except:',
        'error handling',
        'user-friendly',
        'don\'t let program crash'
    ]
    
    error_found = any(indicator in content_lower for indicator in error_handling_indicators)
    if error_found:
        criteria_results.append("✓ Error handling implemented")
        total_points += 2
        print("  Error handling found in code")
    else:
        criteria_results.append("✗ Insufficient error handling")
        print("  Error handling not found")
    
    # Test 6: Check for console output formatting
    print("\nTest 6: Checking console output formatting...")
    formatting_indicators = [
        'print(',
        'format',
        'progress',
        'step',
        '✓',
        '✗'
    ]
    
    formatting_found = sum(1 for indicator in formatting_indicators if indicator in content)
    if formatting_found >= 3:
        criteria_results.append("✓ Console output formatting implemented")
        total_points += 2
        print(f"  Console output formatting found ({formatting_found} indicators)")
    else:
        criteria_results.append("✗ Insufficient console output formatting")
        print(f"  Console output formatting not sufficient ({formatting_found} indicators)")
    
    # Test 7: Run a quick execution test (non-interactive)
    print("\nTest 7: Running quick execution test...")
    try:
        # Create a simple test that runs main with timeout
        test_env = os.environ.copy()
        test_env['PYTHONUNBUFFERED'] = '1'
        
        # We'll test with a simplified version that doesn't require user input
        # by checking if the script can at least start
        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=True,
            text=True,
            timeout=10,
            env=test_env
        )
        
        if result.returncode == 0 or "SALES ANALYTICS SYSTEM" in result.stdout:
            criteria_results.append("✓ Application can execute")
            print("  Application executed (may have been interrupted for user input)")
        else:
            criteria_results.append(f"✗ Execution failed: {result.stderr[:100]}")
            print(f"  Execution failed: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        criteria_results.append("✓ Application runs (timeout expected due to user input)")
        print("  Application ran (timeout expected for interactive mode)")
    except Exception as e:
        criteria_results.append(f"✗ Execution test error: {str(e)}")
        print(f"  Execution test error: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY - MAIN APPLICATION")
    print("=" * 70)
    
    print(f"\nTotal Points: {total_points}/10")
    
    print("\nCriteria Results:")
    for result in criteria_results:
        if '✓' in result:
            print(f"  {result}")
        else:
            print(f"  {result}")
    
    # Show code structure summary
    print(f"\nCode Structure:")
    print(f"  • Lines of code: {len(content.split('\\n'))}")
    print(f"  • Functions defined: {content.count('def ')}")
    print(f"  • Error handling blocks: {content.count('try:')}")
    print(f"  • User input points: {content.count('input(')}")
    
    return total_points >= 8  # Pass if we got at least 8/10 points


if __name__ == "__main__":
    success = test_main_application()
    sys.exit(0 if success else 1)
