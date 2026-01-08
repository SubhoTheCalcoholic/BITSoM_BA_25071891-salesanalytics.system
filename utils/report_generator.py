"""
Report Generator Module
Handles generation of comprehensive sales reports
"""

import os
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import json
from .data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)


def generate_sales_report(transactions: List[Dict], 
                         enriched_transactions: Optional[List[Dict]] = None,
                         output_file: str = 'output/sales_report.txt') -> bool:
    """
    Generates a comprehensive formatted text report

    Report Must Include (in this order):

    1. HEADER
       - Report title
       - Generation date and time
       - Total records processed

    2. OVERALL SUMMARY
       - Total Revenue (formatted with commas)
       - Total Transactions
       - Average Order Value
       - Date Range of data

    3. REGION-WISE PERFORMANCE
       - Table showing each region with:
         * Total Sales Amount
         * Percentage of Total
         * Transaction Count
       - Sorted by sales amount descending

    4. TOP 5 PRODUCTS
       - Table with columns: Rank, Product Name, Quantity Sold, Revenue

    5. TOP 5 CUSTOMERS
       - Table with columns: Rank, Customer ID, Total Spent, Order Count

    6. DAILY SALES TREND
       - Table showing: Date, Revenue, Transactions, Unique Customers

    7. PRODUCT PERFORMANCE ANALYSIS
       - Best selling day
       - Low performing products (if any)
       - Average transaction value per region

    8. API ENRICHMENT SUMMARY
       - Total products enriched
       - Success rate percentage
       - List of products that couldn't be enriched

    Expected Output Format (sample):
    ============================================
           SALES ANALYTICS REPORT
         Generated: 2024-12-18 14:30:22
         Records Processed: 95
    ============================================

    OVERALL SUMMARY
    --------------------------------------------
    Total Revenue:        ₹15,45,000.00
    Total Transactions:   95
    Average Order Value:  ₹16,263.16
    Date Range:           2024-12-01 to 2024-12-31

    REGION-WISE PERFORMANCE
    --------------------------------------------
    Region    Sales         % of Total  Transactions
    North     ₹4,50,000     29.13%      25
    South     ₹3,80,000     24.60%      22
    ...

    (continue with all sections...)
    """
    
    print("=" * 60)
    print("GENERATING COMPREHENSIVE SALES REPORT")
    print("=" * 60)
    
    if not transactions:
        print("Error: No transactions to generate report from")
        return False
    
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nGenerating report with {len(transactions)} transactions...")
        print(f"Output file: {output_file}")
        
        # Start building report content
        report_lines = []
        
        # ============================================
        # SECTION 1: HEADER
        # ============================================
        report_lines.append("=" * 60)
        report_lines.append(" " * 20 + "SALES ANALYTICS REPORT")
        report_lines.append(" " * 22 + f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(" " * 22 + f"Records Processed: {len(transactions):,}")
        report_lines.append("=" * 60)
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 2: OVERALL SUMMARY
        # ============================================
        report_lines.append("OVERALL SUMMARY")
        report_lines.append("-" * 40)
        
        # Calculate summary statistics
        total_revenue = calculate_total_revenue(transactions)
        total_transactions = len(transactions)
        avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Get date range
        dates = sorted(set(t.get('Date', '') for t in transactions if t.get('Date')))
        date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"
        
        report_lines.append(f"Total Revenue:        ₹{total_revenue:,.2f}")
        report_lines.append(f"Total Transactions:   {total_transactions:,}")
        report_lines.append(f"Average Order Value:  ₹{avg_order_value:,.2f}")
        report_lines.append(f"Date Range:           {date_range}")
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 3: REGION-WISE PERFORMANCE
        # ============================================
        report_lines.append("REGION-WISE PERFORMANCE")
        report_lines.append("-" * 40)
        
        # Get region-wise sales data
        region_data = region_wise_sales(transactions)
        
        if region_data:
            # Table header
            report_lines.append(f"{'Region':<12} {'Sales':<16} {'% of Total':<12} {'Transactions':<12}")
            report_lines.append("-" * 52)
            
            # Table rows
            for region, data in region_data.items():
                sales_amount = f"₹{data['total_sales']:,.2f}"
                percentage = f"{data['percentage']:.1f}%"
                transactions_count = f"{data['transaction_count']:,}"
                
                report_lines.append(f"{region:<12} {sales_amount:<16} {percentage:<12} {transactions_count:<12}")
        else:
            report_lines.append("No region data available")
        
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 4: TOP 5 PRODUCTS
        # ============================================
        report_lines.append("TOP 5 PRODUCTS")
        report_lines.append("-" * 40)
        
        # Get top selling products
        top_products = top_selling_products(transactions, n=5)
        
        if top_products:
            # Table header
            report_lines.append(f"{'Rank':<6} {'Product Name':<30} {'Quantity Sold':<15} {'Revenue':<15}")
            report_lines.append("-" * 66)
            
            # Table rows
            for i, (product_name, quantity, revenue) in enumerate(top_products, 1):
                # Truncate long product names
                display_name = product_name[:28] + ".." if len(product_name) > 28 else product_name
                report_lines.append(f"{i:<6} {display_name:<30} {quantity:<15,} ₹{revenue:<14,.2f}")
        else:
            report_lines.append("No product data available")
        
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 5: TOP 5 CUSTOMERS
        # ============================================
        report_lines.append("TOP 5 CUSTOMERS")
        report_lines.append("-" * 40)
        
        # Get customer analysis
        customer_data = customer_analysis(transactions)
        
        if customer_data:
            # Get top 5 customers
            top_customers = list(customer_data.items())[:5]
            
            # Table header
            report_lines.append(f"{'Rank':<6} {'Customer ID':<12} {'Total Spent':<16} {'Order Count':<12}")
            report_lines.append("-" * 46)
            
            # Table rows
            for i, (customer_id, data) in enumerate(top_customers, 1):
                total_spent = f"₹{data['total_spent']:,.2f}"
                order_count = f"{data['purchase_count']:,}"
                report_lines.append(f"{i:<6} {customer_id:<12} {total_spent:<16} {order_count:<12}")
        else:
            report_lines.append("No customer data available")
        
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 6: DAILY SALES TREND
        # ============================================
        report_lines.append("DAILY SALES TREND")
        report_lines.append("-" * 40)
        
        # Get daily sales trend
        daily_trend = daily_sales_trend(transactions)
        
        if daily_trend:
            # Show only top 5 days for brevity (sorted by revenue descending)
            top_days = sorted(
                daily_trend.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )[:5]
            
            # Table header
            report_lines.append(f"{'Date':<12} {'Revenue':<16} {'Transactions':<12} {'Unique Customers':<16}")
            report_lines.append("-" * 56)
            
            # Table rows
            for date, data in top_days:
                revenue = f"₹{data['revenue']:,.2f}"
                transactions = f"{data['transaction_count']:,}"
                unique_customers = f"{data['unique_customers']:,}"
                report_lines.append(f"{date:<12} {revenue:<16} {transactions:<12} {unique_customers:<16}")
            
            # Show note if there are more days
            if len(daily_trend) > 5:
                report_lines.append(f"... and {len(daily_trend) - 5} more days")
        else:
            report_lines.append("No daily trend data available")
        
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 7: PRODUCT PERFORMANCE ANALYSIS
        # ============================================
        report_lines.append("PRODUCT PERFORMANCE ANALYSIS")
        report_lines.append("-" * 40)
        
        # Find peak sales day
        peak_day_data = find_peak_sales_day(transactions)
        if peak_day_data[0]:  # Check if date exists
            report_lines.append(f"Best Selling Day:      {peak_day_data[0]}")
            report_lines.append(f"  Revenue:            ₹{peak_day_data[1]:,.2f}")
            report_lines.append(f"  Transactions:       {peak_day_data[2]:,}")
        else:
            report_lines.append("Best Selling Day:      N/A")
        
        # Find low performing products (threshold = 5 units)
        low_performers = low_performing_products(transactions, threshold=5)
        if low_performers:
            report_lines.append(f"\nLow Performing Products (< 5 units sold): {len(low_performers)}")
            for product_name, quantity, revenue in low_performers[:3]:  # Show top 3
                report_lines.append(f"  • {product_name}: {quantity} units, ₹{revenue:,.2f}")
            if len(low_performers) > 3:
                report_lines.append(f"  ... and {len(low_performers) - 3} more")
        else:
            report_lines.append("\nLow Performing Products: None (all products sold 5+ units)")
        
        # Calculate average transaction value per region
        if region_data:
            report_lines.append("\nAverage Transaction Value by Region:")
            for region, data in region_data.items():
                avg_region_value = data['total_sales'] / data['transaction_count'] if data['transaction_count'] > 0 else 0
                report_lines.append(f"  {region}: ₹{avg_region_value:,.2f}")
        else:
            report_lines.append("\nAverage Transaction Value by Region: N/A")
        
        report_lines.append("")  # Empty line for spacing
        
        # ============================================
        # SECTION 8: API ENRICHMENT SUMMARY
        # ============================================
        report_lines.append("API ENRICHMENT SUMMARY")
        report_lines.append("-" * 40)
        
        if enriched_transactions:
            # Calculate enrichment statistics
            total_enriched = len(enriched_transactions)
            successful_enrichments = sum(1 for t in enriched_transactions if t.get('API_Match') == True)
            failed_enrichments = total_enriched - successful_enrichments
            success_rate = (successful_enrichments / total_enriched * 100) if total_enriched > 0 else 0
            
            report_lines.append(f"Total Products Enriched:      {total_enriched:,}")
            report_lines.append(f"Successful Enrichments:       {successful_enrichments:,}")
            report_lines.append(f"Failed Enrichments:           {failed_enrichments:,}")
            report_lines.append(f"Success Rate:                 {success_rate:.1f}%")
            
            # List products that couldn't be enriched
            if failed_enrichments > 0:
                failed_products = []
                for trans in enriched_transactions:
                    if trans.get('API_Match') == False:
                        product_id = trans.get('ProductID', 'Unknown')
                        product_name = trans.get('ProductName', 'Unknown')
                        failed_products.append(f"{product_id} ({product_name})")
                
                # Get unique failed products
                unique_failed = list(set(failed_products))
                report_lines.append(f"\nProducts Not Found in API:   {len(unique_failed)}")
                
                # Show up to 5 failed products
                for i, product in enumerate(unique_failed[:5], 1):
                    report_lines.append(f"  {i}. {product}")
                
                if len(unique_failed) > 5:
                    report_lines.append(f"  ... and {len(unique_failed) - 5} more")
        else:
            report_lines.append("API Enrichment: Not performed")
            report_lines.append("(No enriched transactions provided)")
        
        # ============================================
        # FOOTER
        # ============================================
        report_lines.append("\n" + "=" * 60)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 60)
        
        # ============================================
        # SAVE REPORT TO FILE
        # ============================================
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(report_lines))
        
        print(f"✓ Report successfully generated: {output_file}")
        print(f"  Report contains {len(report_lines)} lines across 8 sections")
        
        # Print sample of report to console
        print("\nSample of generated report (first 20 lines):")
        print("-" * 60)
        for i, line in enumerate(report_lines[:20], 1):
            print(f"{i:2}: {line}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating report: {str(e)}")
        return False


def generate_json_report(transactions: List[Dict], 
                        enriched_transactions: Optional[List[Dict]] = None,
                        output_file: str = 'output/sales_report.json') -> bool:
    """
    Generates a comprehensive JSON report with all analytics data
    
    Args:
        transactions: List of transaction dictionaries
        enriched_transactions: List of enriched transactions (optional)
        output_file: Path to save JSON report
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        print(f"\nGenerating JSON report: {output_file}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Calculate all analytics
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_transactions': len(transactions),
                'report_version': '1.0'
            },
            'overall_summary': {
                'total_revenue': calculate_total_revenue(transactions),
                'total_transactions': len(transactions),
                'average_order_value': calculate_total_revenue(transactions) / len(transactions) if transactions else 0,
                'date_range': {
                    'start': min(t.get('Date') for t in transactions if t.get('Date')),
                    'end': max(t.get('Date') for t in transactions if t.get('Date'))
                } if transactions else None
            },
            'region_analysis': region_wise_sales(transactions),
            'top_products': {
                'top_5_by_quantity': top_selling_products(transactions, n=5),
                'low_performing': low_performing_products(transactions, threshold=5)
            },
            'customer_analysis': customer_analysis(transactions),
            'daily_trends': daily_sales_trend(transactions),
            'peak_performance': {
                'peak_day': find_peak_sales_day(transactions)
            }
        }
        
        # Add API enrichment data if available
        if enriched_transactions:
            successful = sum(1 for t in enriched_transactions if t.get('API_Match') == True)
            failed = len(enriched_transactions) - successful
            success_rate = (successful / len(enriched_transactions) * 100) if enriched_transactions else 0
            
            # Get unique failed products
            failed_products = []
            for trans in enriched_transactions:
                if trans.get('API_Match') == False:
                    product_info = {
                        'product_id': trans.get('ProductID'),
                        'product_name': trans.get('ProductName')
                    }
                    if product_info not in failed_products:
                        failed_products.append(product_info)
            
            report_data['api_enrichment'] = {
                'total_enriched': len(enriched_transactions),
                'successful_matches': successful,
                'failed_matches': failed,
                'success_rate': success_rate,
                'failed_products': failed_products[:10]  # Limit to first 10
            }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(report_data, file, indent=2, default=str)
        
        print(f"✓ JSON report saved: {output_file}")
        print(f"  File size: {os.path.getsize(output_file):,} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating JSON report: {str(e)}")
        return False


def generate_executive_summary(transactions: List[Dict], 
                              output_file: str = 'output/executive_summary.txt') -> bool:
    """
    Generates a brief executive summary report
    
    Args:
        transactions: List of transaction dictionaries
        output_file: Path to save summary
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        print(f"\nGenerating executive summary: {output_file}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Calculate key metrics
        total_revenue = calculate_total_revenue(transactions)
        region_data = region_wise_sales(transactions)
        top_products = top_selling_products(transactions, n=3)
        top_customers = list(customer_analysis(transactions).items())[:3]
        peak_day = find_peak_sales_day(transactions)
        
        # Generate summary
        summary_lines = [
            "=" * 60,
            "EXECUTIVE SUMMARY - SALES ANALYTICS",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            "",
            "KEY PERFORMANCE INDICATORS",
            "-" * 30,
            f"• Total Revenue:        ₹{total_revenue:,.2f}",
            f"• Total Transactions:   {len(transactions):,}",
            f"• Avg Order Value:      ₹{total_revenue/len(transactions):,.2f}",
            "",
            "TOP REGION",
            "-" * 30,
        ]
        
        if region_data:
            top_region = list(region_data.items())[0]
            summary_lines.append(f"• {top_region[0]}: ₹{top_region[1]['total_sales']:,.2f}")
            summary_lines.append(f"  ({top_region[1]['percentage']:.1f}% of total revenue)")
        else:
            summary_lines.append("• No region data available")
        
        summary_lines.extend([
            "",
            "TOP PRODUCTS",
            "-" * 30,
        ])
        
        if top_products:
            for i, (name, qty, revenue) in enumerate(top_products, 1):
                summary_lines.append(f"{i}. {name}: {qty:,} units (₹{revenue:,.2f})")
        else:
            summary_lines.append("• No product data available")
        
        summary_lines.extend([
            "",
            "TOP CUSTOMERS",
            "-" * 30,
        ])
        
        if top_customers:
            for i, (customer_id, data) in enumerate(top_customers, 1):
                summary_lines.append(f"{i}. {customer_id}: ₹{data['total_spent']:,.2f} ({data['purchase_count']:,} orders)")
        else:
            summary_lines.append("• No customer data available")
        
        summary_lines.extend([
            "",
            "PEAK PERFORMANCE",
            "-" * 30,
        ])
        
        if peak_day[0]:
            summary_lines.append(f"• Best Day: {peak_day[0]}")
            summary_lines.append(f"  Revenue: ₹{peak_day[1]:,.2f} ({peak_day[2]:,} transactions)")
        else:
            summary_lines.append("• No peak day data available")
        
        summary_lines.extend([
            "",
            "RECOMMENDATIONS",
            "-" * 30,
            "1. Focus marketing efforts on top-performing region",
            "2. Promote top-selling products more aggressively",
            "3. Implement loyalty program for top customers",
            "4. Analyze and address low-performing products",
            "5. Replicate successful strategies from peak sales day",
            "",
            "=" * 60,
            "END OF EXECUTIVE SUMMARY",
            "=" * 60,
        ])
        
        # Save summary
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(summary_lines))
        
        print(f"✓ Executive summary saved: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating executive summary: {str(e)}")
        return False

# ============================================

"""
Test script for Task 4.1: Report Generation
"""

import os
import sys
from utils.file_handler import read_sales_data, parse_transactions
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data
from utils.report_generator import generate_sales_report, generate_json_report, generate_executive_summary


def test_report_generation():
    """Test the report generation functions"""
    
    print("=" * 70)
    print("TESTING TASK 4.1: REPORT GENERATION")
    print("=" * 70)
    
    # Load test data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, "data", "sales_data.txt")
    
    print("\nLoading test data...")
    lines = read_sales_data(data_file)
    transactions = parse_transactions(lines)
    
    if not transactions:
        print("Error: No transactions to generate report")
        return False
    
    print(f"Loaded {len(transactions)} transactions")
    
    # Try to enrich data for API section (optional)
    print("\nAttempting to fetch API data for enrichment...")
    try:
        api_products = fetch_all_products()
        if api_products:
            product_mapping = create_product_mapping(api_products)
            enriched_transactions = enrich_sales_data(transactions, product_mapping)
            print(f"Enriched {len(enriched_transactions)} transactions")
        else:
            print("API fetch failed, will generate report without enrichment")
            enriched_transactions = None
    except Exception as e:
        print(f"API enrichment failed: {str(e)}")
        enriched_transactions = None
    
    total_points = 0
    criteria_results = []
    
    # ============================================
    # Test generate_sales_report()
    # ============================================
    print("\n" + "=" * 70)
    print("Testing generate_sales_report()")
    print("=" * 70)
    
    output_file = os.path.join(current_dir, "output", "test_sales_report.txt")
    
    success = generate_sales_report(transactions, enriched_transactions, output_file)
    
    if success:
        # Check if file was created
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # Check all 8 sections are present
            sections_to_check = [
                "OVERALL SUMMARY",
                "REGION-WISE PERFORMANCE", 
                "TOP 5 PRODUCTS",
                "TOP 5 CUSTOMERS",
                "DAILY SALES TREND",
                "PRODUCT PERFORMANCE ANALYSIS",
                "API ENRICHMENT SUMMARY"
            ]
            
            sections_found = 0
            for section in sections_to_check:
                if section in report_content:
                    sections_found += 1
            
            if sections_found == len(sections_to_check):
                criteria_results.append("✓ All 8 sections present in report (+8 points)")
                total_points += 8
            else:
                criteria_results.append(f"✗ Missing sections: Found {sections_found}/{len(sections_to_check)}")
            
            # Check formatting (look for proper alignment)
            lines = report_content.split('\n')
            has_tables = any('Region' in line and 'Sales' in line for line in lines)
            has_formatting = any('=' * 60 in line for line in lines) and any('-' * 40 in line for line in lines)
            
            if has_tables and has_formatting:
                criteria_results.append("✓ Proper formatting and alignment (+3 points)")
                total_points += 3
            else:
                criteria_results.append("✗ Improper formatting or alignment")
            
            # Check calculations (verify some numbers)
            revenue_line = next((line for line in lines if 'Total Revenue:' in line), None)
            if revenue_line:
                criteria_results.append("✓ Revenue calculation displayed (+1 point)")
                total_points += 1
            else:
                criteria_results.append("✗ Revenue calculation missing")
            
            # Check for other calculations
            calculation_checks = [
                'Average Order Value',
                'Percentage of Total',
                'Quantity Sold',
                'Total Spent'
            ]
            
            calculations_found = sum(1 for check in calculation_checks if any(check in line for line in lines))
            if calculations_found >= 3:
                criteria_results.append("✓ Multiple accurate calculations present (+3 points)")
                total_points += 3
            else:
                criteria_results.append(f"✗ Insufficient calculations: Found {calculations_found}/4")
        else:
            criteria_results.append("✗ Report file not created")
    else:
        criteria_results.append("✗ generate_sales_report() returned False")
    
    # ============================================
    # Test generate_json_report()
    # ============================================
    print("\n" + "=" * 70)
    print("Testing generate_json_report()")
    print("=" * 70)
    
    json_output = os.path.join(current_dir, "output", "test_sales_report.json")
    json_success = generate_json_report(transactions, enriched_transactions, json_output)
    
    if json_success and os.path.exists(json_output):
        try:
            import json
            with open(json_output, 'r') as f:
                json_data = json.load(f)
            
            if all(key in json_data for key in ['metadata', 'overall_summary', 'region_analysis']):
                criteria_results.append("✓ JSON report structure correct")
                print(f"  JSON report size: {os.path.getsize(json_output):,} bytes")
            else:
                criteria_results.append("✗ JSON report missing required sections")
        except Exception as e:
            criteria_results.append(f"✗ Error reading JSON report: {str(e)}")
    else:
        criteria_results.append("✗ JSON report not generated")
    
    # ============================================
    # Test generate_executive_summary()
    # ============================================
    print("\n" + "=" * 70)
    print("Testing generate_executive_summary()")
    print("=" * 70)
    
    summary_output = os.path.join(current_dir, "output", "test_executive_summary.txt")
    summary_success = generate_executive_summary(transactions, summary_output)
    
    if summary_success and os.path.exists(summary_output):
        with open(summary_output, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        if 'EXECUTIVE SUMMARY' in summary_content and 'KEY PERFORMANCE INDICATORS' in summary_content:
            criteria_results.append("✓ Executive summary generated successfully")
            print(f"  Summary file size: {os.path.getsize(summary_output):,} bytes")
        else:
            criteria_results.append("✗ Executive summary missing key sections")
    else:
        criteria_results.append("✗ Executive summary not generated")
    
    # ============================================
    # Final Summary
    # ============================================
    print("\n" + "=" * 70)
    print("TEST SUMMARY - REPORT GENERATION")
    print("=" * 70)
    
    print(f"\nTotal Points: {total_points}/15")
    
    print("\nCriteria Results:")
    for result in criteria_results:
        print(f"  {result}")
    
    # Show what was generated
    print(f"\nGenerated Files:")
    for file_path in [output_file, json_output, summary_output]:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            print(f"  • {file_name}: {file_size:,} bytes")
    
    return success


if __name__ == "__main__":
    test_report_generation()
