#!/usr/bin/env python3
"""
SyndicAgent Demo Script

This script demonstrates how to use SyndicAgent to:
1. Fetch data from Agworld API (or use mock data)
2. Process the data
3. Generate reports

Usage: python demo.py
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def print_banner():
    """Print a welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                      SyndicAgent Demo                       ║
║              Agworld Data Processing & Reporting            ║
╚══════════════════════════════════════════════════════════════╝
    """)

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def demo_data_collection():
    """Demonstrate data collection from Agworld API"""
    print_section("📊 Data Collection")
    
    from app.services.agworld_client import agworld_client
    
    print("Connecting to Agworld API...")
    print("(Note: Using mock data since no API token is configured)")
    
    # Collect data from different endpoints
    data_sources = [
        ('Fields', agworld_client.get_fields),
        ('Crops', agworld_client.get_crops),
        ('Activities', agworld_client.get_activities),
        ('Companies', agworld_client.get_companies),
        ('Farms', agworld_client.get_farms),
        ('Seasons', agworld_client.get_seasons)
    ]
    
    collected_data = {}
    
    for name, method in data_sources:
        try:
            data = method()
            collected_data[name.lower()] = data
            print(f"✅ {name}: {len(data)} records retrieved")
            
            # Show sample data
            if data and len(data) > 0:
                sample = data[0]
                print(f"   Sample: {sample.get('name', sample.get('title', sample.get('type', 'N/A')))}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            collected_data[name.lower()] = []
    
    return collected_data

def demo_data_processing(collected_data):
    """Demonstrate data processing"""
    print_section("⚙️  Data Processing")
    
    from app.services.processor import processor
    
    processed_data = []
    
    # Define data type mappings
    data_type_mapping = {
        'fields': 'field',
        'crops': 'crop',
        'activities': 'activity',
        'companies': 'company',
        'farms': 'farm',
        'seasons': 'season'
    }
    
    print("Processing collected data...")
    
    for data_source, data_type in data_type_mapping.items():
        if data_source in collected_data and collected_data[data_source]:
            items = collected_data[data_source]
            print(f"\n🔄 Processing {len(items)} {data_type} records...")
            
            for i, item in enumerate(items[:3], 1):  # Process first 3 for demo
                try:
                    result = processor.process_agworld_data(item, data_type)
                    processed_data.append(result)
                    
                    # Show processing result
                    summary = result.get('processed_data', {}).get('summary', 'No summary')
                    print(f"   {i}. {summary}")
                    
                except Exception as e:
                    print(f"   {i}. Error processing {data_type}: {e}")
    
    # Aggregate the processed data
    if processed_data:
        print(f"\n📈 Aggregating {len(processed_data)} processed records...")
        aggregated = processor.aggregate_data(processed_data)
        
        print(f"✅ Aggregation complete:")
        print(f"   Total records: {aggregated.get('total_records', 0)}")
        print(f"   Data types: {list(aggregated.get('data_types', {}).keys())}")
        
        # Show type breakdown
        for data_type, count in aggregated.get('data_types', {}).items():
            print(f"   - {data_type}: {count} records")
    
    return processed_data

def demo_report_generation(processed_data):
    """Demonstrate report generation"""
    print_section("📄 Report Generation")
    
    if not processed_data:
        print("❌ No processed data available for reporting")
        return None
    
    from app.services.reporter import reporter
    
    print("Creating summary report...")
    
    try:
        # Create summary report
        report_data = reporter.create_summary_report(processed_data)
        
        print("✅ Summary report created:")
        print(f"   Title: {report_data.get('title', 'Unknown')}")
        print(f"   Status: {report_data.get('status', 'Unknown')}")
        print(f"   Type: {report_data.get('report_type', 'Unknown')}")
        
        # Generate PDF report
        print("\n📄 Generating PDF report...")
        result = reporter.generate_report(report_data, format_type="pdf")
        
        if result.get('success'):
            pdf_path = result.get('pdf_path')
            if pdf_path and os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ PDF report generated successfully!")
                print(f"   File: {pdf_path}")
                print(f"   Size: {file_size:,} bytes")
                
                # Show report content preview
                print("\n📖 Report Content Preview:")
                content = report_data.get('content', '')
                preview = content.split('\n')[:8]  # First 8 lines
                for line in preview:
                    print(f"   {line}")
                if len(content.split('\n')) > 8:
                    print("   ...")
                
                return pdf_path
            else:
                print("❌ PDF file was not created")
        else:
            errors = result.get('errors', [])
            print(f"❌ PDF generation failed: {', '.join(errors)}")
    
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    return None

def demo_configuration():
    """Show configuration information"""
    print_section("⚙️  Configuration")
    
    from app.config import settings
    
    print("Current configuration:")
    print(f"   API base URL: {settings.AGWORLD_API_BASE_URL}")
    print(f"   Redis URL: {settings.REDIS_URL}")
    print(f"   Database URL: {settings.DATABASE_URL}")
    
    # Check environment variables
    api_token = os.getenv('AGWORLD_API_TOKEN') or settings.AGWORLD_API_KEY
    if api_token:
        print(f"   API Token: {'*' * max(0, len(api_token) - 4)}{api_token[-4:] if len(api_token) >= 4 else api_token}")
        print("   ✅ Ready for live API calls")
    else:
        print("   API Token: Not configured")
        print("   ⚠️  Using mock data fallback")
    
    print("\n📝 To use with real Agworld API:")
    print("   1. Get API token from: https://us.agworld.co/user_api/v1/docs")
    print("   2. Set environment variable: export AGWORLD_API_TOKEN='your_token'")
    print("   3. Re-run this demo")

def main():
    """Run the complete demo"""
    print_banner()
    
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        # Step 1: Show configuration
        demo_configuration()
        
        # Step 2: Collect data
        collected_data = demo_data_collection()
        
        # Step 3: Process data
        processed_data = demo_data_processing(collected_data)
        
        # Step 4: Generate reports
        pdf_path = demo_report_generation(processed_data)
        
        # Summary
        print_section("🎉 Demo Complete")
        
        if processed_data:
            print(f"✅ Successfully processed {len(processed_data)} data records")
        
        if pdf_path:
            print(f"✅ Generated PDF report: {pdf_path}")
            print("\n💡 You can open the PDF file to view the complete report")
        
        print("\n🚀 Next steps:")
        print("   • Configure your Agworld API token for live data")
        print("   • Set up Redis for production caching")
        print("   • Customize report templates")
        print("   • Set up email notifications")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Check that all dependencies are installed")
        print("   • Verify the app directory structure")
        print("   • Run: python test_local.py")
    
    print(f"\nDemo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
