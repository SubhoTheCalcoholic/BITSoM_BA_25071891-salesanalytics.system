"""
Utilities package for Sales Data Analytics System

This package contains all the core modules for handling sales data:
- File operations and I/O
- Data processing, cleaning, and analysis
- External API integration
- Report generation
"""

from .file_handler import FileHandler, read_sales_data, parse_transactions
from .data_processor import DataProcessor, validate_and_filter
from .api_handler import APIHandler, fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data
from .report_generator import generate_sales_report, generate_json_report, generate_executive_summary

__version__ = "1.0.0"
__author__ = "Sales Analytics Team"
__all__ = [
    'FileHandler', 'read_sales_data', 'parse_transactions',
    'DataProcessor', 'validate_and_filter',
    'APIHandler', 'fetch_all_products', 'create_product_mapping', 
    'enrich_sales_data', 'save_enriched_data',
    'generate_sales_report', 'generate_json_report', 'generate_executive_summary'
]


def get_version():
    """Return the current version of the utils package"""
    return __version__


def get_available_modules():
    """Return list of available modules in the utils package"""
    return {
        'file_handler': 'Handles file operations, reading, writing, and encoding',
        'data_processor': 'Processes, cleans, validates, and analyzes sales data',
        'api_handler': 'Manages external API integration for product information',
        'report_generator': 'Generates comprehensive reports in multiple formats'
    }


def initialize_utils():
    """Initialize all utility modules with default configurations"""
    print(f"Initializing Sales Analytics Utilities v{__version__}")
    print("Available modules:")
    for module_name, description in get_available_modules().items():
        print(f"  - {module_name}: {description}")
    return True


# Optional: Add any package-level configuration or constants
DEFAULT_DELIMITER = '|'
SUPPORTED_ENCODINGS = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
VALID_REGIONS = ['North', 'South', 'East', 'West']
MIN_QUANTITY = 1
MIN_PRICE = 0.01

# Export constants
__all__.extend([
    'DEFAULT_DELIMITER',
    'SUPPORTED_ENCODINGS',
    'VALID_REGIONS',
    'MIN_QUANTITY',
    'MIN_PRICE',
    'get_version',
    'get_available_modules',
    'initialize_utils'
])


# Package initialization message
if __name__ != "__main__":
    # This runs when the package is imported
    pass
else:
    # Test code when the module is run directly
    print("Sales Analytics Utilities Package")
    print(f"Version: {get_version()}")
    print(f"Author: {__author__}")
    print("\nAvailable modules:")
    for name, desc in get_available_modules().items():
        print(f"  {name}: {desc}")
