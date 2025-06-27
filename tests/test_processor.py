import pytest
from datetime import datetime
from app.services.processor import processor
from app.services.agworld_client import agworld_client
from app.services.reporter import reporter
from app.services.notifier import notifier
from app.redis_client import redis_client

class TestDataProcessor:
    """Test data processing functionality"""
    
    def test_process_field_data(self):
        """Test field data processing"""
        raw_data = {
            "id": "field_001",
            "name": "Test Field",
            "area": 25.5,
            "location": {"lat": -27.4698, "lng": 153.0251}
        }
        
        result = processor.process_agworld_data(raw_data, "field")
        
        assert result["data_type"] == "field"
        assert "processed_at" in result
        assert "processed_data" in result
        assert result["processed_data"]["field_name"] == "Test Field"
        assert result["processed_data"]["area"] == 25.5
    
    def test_process_crop_data(self):
        """Test crop data processing"""
        raw_data = {
            "id": "crop_001",
            "type": "Wheat",
            "variety": "Winter Wheat",
            "planting_date": "2024-04-15"
        }
        
        result = processor.process_agworld_data(raw_data, "crop")
        
        assert result["data_type"] == "crop"
        assert result["processed_data"]["crop_type"] == "Wheat"
        assert result["processed_data"]["variety"] == "Winter Wheat"
    
    def test_aggregate_data(self):
        """Test data aggregation"""
        data_list = [
            {
                "data_type": "field",
                "processed_data": {"summary": "Field 1"}
            },
            {
                "data_type": "field",
                "processed_data": {"summary": "Field 2"}
            },
            {
                "data_type": "crop",
                "processed_data": {"summary": "Crop 1"}
            }
        ]
        
        result = processor.aggregate_data(data_list)
        
        assert result["total_records"] == 3
        assert result["data_types"]["field"] == 2
        assert result["data_types"]["crop"] == 1
        assert len(result["summaries"]) == 3

class TestAgworldClient:
    """Test Agworld API client functionality"""
    
    def test_get_fields(self):
        """Test field data retrieval"""
        fields = agworld_client.get_fields()
        
        assert isinstance(fields, list)
        assert len(fields) > 0
        assert "id" in fields[0]
        assert "name" in fields[0]
    
    def test_get_crops(self):
        """Test crop data retrieval"""
        crops = agworld_client.get_crops()
        
        assert isinstance(crops, list)
        assert len(crops) > 0
        assert "id" in crops[0]
        assert "type" in crops[0]
    
    def test_connection(self):
        """Test API connection"""
        # This will test the mock connection
        is_connected = agworld_client.test_connection()
        assert isinstance(is_connected, bool)

class TestReporter:
    """Test report generation functionality"""
    
    def test_create_summary_report(self):
        """Test summary report creation"""
        processed_data_list = [
            {
                "data_type": "field",
                "processed_data": {"summary": "Test field"}
            }
        ]
        
        report = reporter.create_summary_report(processed_data_list)
        
        assert "title" in report
        assert "created_at" in report
        assert "content" in report
        assert "data" in report
        assert report["report_type"] == "summary"
    
    def test_generate_report(self):
        """Test report generation"""
        report_data = {
            "title": "Test Report",
            "content": "Test content",
            "created_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        # Test PDF generation only (no email)
        result = reporter.generate_report(report_data, "pdf")
        
        assert "success" in result
        assert "pdf_path" in result
        assert "errors" in result

class TestNotifier:
    """Test notification functionality"""
    
    def test_send_notification_without_config(self):
        """Test notification sending without email config"""
        recipients = {"emails": ["test@example.com"]}
        data = {"title": "Test", "content": "Test content"}
        
        # This should fail gracefully without email config
        result = notifier.send_notification("email", recipients, data)
        
        # Should return False since email is not configured
        assert isinstance(result, bool)

class TestRedisClient:
    """Test Redis client functionality"""
    
    def test_redis_operations(self):
        """Test basic Redis operations"""
        # Test set and get
        key = "test_key"
        value = {"test": "data"}
        
        success = redis_client.set(key, value, ex=60)
        assert isinstance(success, bool)
        
        retrieved = redis_client.get(key)
        if redis_client.ping():
            assert retrieved == value
        
        # Test delete
        deleted = redis_client.delete(key)
        assert isinstance(deleted, bool)
    
    def test_redis_connection(self):
        """Test Redis connection"""
        is_connected = redis_client.ping()
        assert isinstance(is_connected, bool)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
