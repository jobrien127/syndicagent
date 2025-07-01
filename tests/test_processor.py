import pytest
from unittest.mock import Mock, patch
from app.services.processor import processor


class TestDataProcessor:
    """Tests for DataProcessor class"""
    
    def test_process_field_data(self):
        """Test field data processing"""
        raw_data = {
            "id": "field_123",
            "name": "North Field",
            "area": 100.5,
            "farm_id": "farm_456",
            "description": "Main crop field",
            "cropping_method": "conventional",
            "crops": ["corn", "soybeans"],
            "chemical_cost": 1500.00,
            "fertilizer_cost": 2000.00,
            "seed_cost": 800.00
        }
        
        result = processor._process_field_data(raw_data)
        
        assert result["field_id"] == "field_123"
        assert result["field_name"] == "North Field"
        assert result["area"] == 100.5
        assert result["farm_id"] == "farm_456"
        assert "North Field" in result["summary"]
    
    def test_process_crop_data(self):
        """Test crop data processing"""
        raw_data = {
            "id": "crop_789",
            "type": "corn",
            "variety": "Pioneer 1234",
            "field_id": "field_123",
            "crop_grade": "A",
            "crop_use": "grain",
            "crop_blend": None,
            "planting_date": "2025-04-15",
            "harvest_date": "2025-10-15"
        }
        
        result = processor._process_crop_data(raw_data)
        
        assert result["crop_id"] == "crop_789"
        assert result["crop_type"] == "corn"
        assert result["variety"] == "Pioneer 1234"
        assert result["field_id"] == "field_123"
        assert "corn" in result["summary"]
    
    def test_process_agworld_data(self):
        """Test main processing function"""
        raw_data = {
            "id": "test_123",
            "name": "Test Field",
            "area": 50.0
        }
        
        result = processor.process_agworld_data(raw_data, "field")
        
        assert "processed_at" in result
        assert "data_type" in result
        assert result["data_type"] == "field"
        assert "processed_data" in result
    
    def test_aggregate_data(self):
        """Test data aggregation"""
        data_list = [
            {"field_id": "1", "area": 100, "cost": 1000},
            {"field_id": "2", "area": 150, "cost": 1500},
            {"field_id": "3", "area": 75, "cost": 750}
        ]
        
        result = processor.aggregate_data(data_list)
        
        assert result["total_records"] == 3
        assert "summary" in result
        assert "aggregated_at" in result
    
    @patch('app.redis_client.redis_client.get')
    def test_get_cached_data(self, mock_redis_get):
        """Test cache retrieval"""
        mock_redis_get.return_value = '{"cached": true}'
        
        result = processor.get_cached_data("field", "test_hash")
        
        assert result is not None
        mock_redis_get.assert_called_once()
    
    def test_process_generic_data(self):
        """Test generic data processing fallback"""
        raw_data = {
            "unknown_field": "value",
            "another_field": 123
        }
        
        result = processor._process_generic_data(raw_data)
        
        assert "raw_data" in result
        assert result["raw_data"] == raw_data
        assert "processed_at" in result


if __name__ == "__main__":
    pytest.main([__file__])
