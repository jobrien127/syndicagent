#!/usr/bin/env python3
"""
Test script for local development and testing.
This script can be used to run basic functionality tests without Docker.
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🌾 Agworld Reporter - Local Test")
    print("=" * 60)
    print()

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from app.config import settings
        print("✅ Config module imported successfully")
        
        from app.redis_client import redis_client
        print("✅ Redis client imported successfully")
        
        from app.database import create_tables, get_db
        print("✅ Database module imported successfully")
        
        from app.services.agworld_client import agworld_client
        print("✅ Agworld client imported successfully")
        
        from app.services.processor import processor
        print("✅ Data processor imported successfully")
        
        from app.services.reporter import reporter
        print("✅ Report generator imported successfully")
        
        from app.services.notifier import notifier
        print("✅ Notification service imported successfully")
        
        from app.utils.logger import get_logger
        print("✅ Logger utility imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\nTesting configuration...")
    
    try:
        from app.config import settings
        
        print(f"Database URL: {settings.DATABASE_URL}")
        print(f"Redis URL: {settings.REDIS_URL}")
        print(f"Agworld API Base URL: {settings.AGWORLD_API_BASE_URL}")
        
        # Check if API key is configured
        if settings.AGWORLD_API_KEY:
            print(f"Agworld API Key: {'*' * (len(settings.AGWORLD_API_KEY) - 4)}{settings.AGWORLD_API_KEY[-4:]}")
        else:
            print("Agworld API Key: Not configured (using mock data)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database connection and table creation"""
    print("\nTesting database...")
    
    try:
        from app.database import create_tables
        
        # Try to create tables
        create_tables()
        print("✅ Database tables created/verified successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    print("\nTesting Redis connection...")
    
    try:
        from app.redis_client import redis_client
        
        # Test Redis connection
        if redis_client.ping():
            print("✅ Redis connection successful")
            
            # Test basic operations
            test_key = "test:local_test"
            test_value = {"test": True, "timestamp": datetime.now().isoformat()}
            
            redis_client.set(test_key, test_value, ex=60)
            retrieved = redis_client.get(test_key)
            
            if retrieved and retrieved.get("test"):
                print("✅ Redis set/get operations working")
                redis_client.delete(test_key)
            else:
                print("⚠️ Redis operations may have issues")
                
        else:
            print("⚠️ Redis connection failed - using memory cache fallback")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False

def test_api_client():
    """Test Agworld API client"""
    print("\nTesting Agworld API client...")
    
    try:
        from app.services.agworld_client import agworld_client
        
        # Test connection (will use mock data if no API key)
        connection_ok = agworld_client.test_connection()
        
        if connection_ok:
            print("✅ Agworld API client initialized successfully")
            
            # Test data fetching
            fields = agworld_client.get_fields()
            if fields:
                print(f"✅ Retrieved {len(fields)} field records")
            
            activities = agworld_client.get_activities()
            if activities:
                print(f"✅ Retrieved {len(activities)} activity records")
                
        else:
            print("⚠️ Agworld API connection test failed")
        
        return True
        
    except Exception as e:
        print(f"❌ API client error: {e}")
        return False

def test_data_processing():
    """Test data processing functionality"""
    print("\nTesting data processing...")
    
    try:
        from app.services.processor import processor
        from app.services.agworld_client import agworld_client
        
        # Get some test data
        test_data = agworld_client.get_fields()
        
        if test_data:
            # Process the data
            processed = processor.process_agworld_data(test_data[0], "field")
            
            if processed:
                print("✅ Data processing successful")
                print(f"   Processed field: {processed.get('summary', 'N/A')}")
            else:
                print("⚠️ Data processing returned empty result")
        else:
            print("⚠️ No test data available for processing")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("\nTesting report generation...")
    
    try:
        from app.services.reporter import reporter
        from app.services.agworld_client import agworld_client
        from app.services.processor import processor
        
        # Get and process some test data
        field_data = agworld_client.get_fields()
        
        if field_data:
            processed_data = []
            for field in field_data[:3]:  # Process first 3 fields
                processed = processor.process_agworld_data(field, "field")
                if processed:
                    processed_data.append(processed)
            
            if processed_data:
                # Create a test report
                report_data = reporter.create_summary_report(processed_data)
                
                if report_data:
                    print("✅ Summary report created successfully")
                    print(f"   Report title: {report_data.get('title', 'N/A')}")
                    
                    # Try to generate a file
                    result = reporter.generate_report(report_data, format_type="pdf")
                    
                    if result.get('success'):
                        print("✅ Report file generation successful")
                        if result.get('pdf_path'):
                            print(f"   PDF path: {result['pdf_path']}")
                    else:
                        print("⚠️ Report file generation had issues")
                        
                else:
                    print("⚠️ Summary report creation failed")
            else:
                print("⚠️ No processed data available for reporting")
        else:
            print("⚠️ No field data available for testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return False

def main():
    """Run all tests"""
    print_banner()
    
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Redis", test_redis),
        ("API Client", test_api_client),
        ("Data Processing", test_data_processing),
        ("Report Generation", test_report_generation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print("-" * 50)
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
        print()
    
    # Print summary
    print("=" * 60)
    print("🧪 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print()
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
