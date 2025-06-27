from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from app.utils.logger import LoggerMixin
from app.redis_client import redis_client

class DataProcessor(LoggerMixin):
    """Handles data extraction and transformation logic"""
    
    def __init__(self):
        super().__init__()
        self.cache_ttl = 3600  # 1 hour cache
    
    def process_agworld_data(self, raw_data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Process raw data from Agworld API"""
        try:
            self.log_info(f"Processing {data_type} data")
            
            processed_data = {
                "data_type": data_type,
                "processed_at": datetime.utcnow().isoformat(),
                "source": "agworld",
                "raw_data_hash": hash(json.dumps(raw_data, sort_keys=True)),
                "processed_data": {}
            }
            
            # Basic processing based on data type
            if data_type == "field":
                processed_data["processed_data"] = self._process_field_data(raw_data)
            elif data_type == "crop":
                processed_data["processed_data"] = self._process_crop_data(raw_data)
            elif data_type == "activity":
                processed_data["processed_data"] = self._process_activity_data(raw_data)
            else:
                processed_data["processed_data"] = self._process_generic_data(raw_data)
            
            # Cache processed data
            cache_key = f"processed:{data_type}:{processed_data['raw_data_hash']}"
            redis_client.set(cache_key, processed_data, ex=self.cache_ttl)
            
            self.log_info(f"Successfully processed {data_type} data")
            return processed_data
            
        except Exception as e:
            self.log_error(f"Error processing {data_type} data: {str(e)}")
            raise
    
    def _process_field_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process field-specific data"""
        return {
            "field_id": raw_data.get("id"),
            "field_name": raw_data.get("name"),
            "area": raw_data.get("area"),
            "location": raw_data.get("location"),
            "summary": f"Field: {raw_data.get('name', 'Unknown')} - Area: {raw_data.get('area', 'N/A')}"
        }
    
    def _process_crop_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process crop-specific data"""
        return {
            "crop_id": raw_data.get("id"),
            "crop_type": raw_data.get("type"),
            "variety": raw_data.get("variety"),
            "planting_date": raw_data.get("planting_date"),
            "summary": f"Crop: {raw_data.get('type', 'Unknown')} - Variety: {raw_data.get('variety', 'N/A')}"
        }
    
    def _process_activity_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity-specific data"""
        return {
            "activity_id": raw_data.get("id"),
            "activity_type": raw_data.get("type"),
            "date": raw_data.get("date"),
            "description": raw_data.get("description"),
            "summary": f"Activity: {raw_data.get('type', 'Unknown')} on {raw_data.get('date', 'Unknown date')}"
        }
    
    def _process_generic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic data when type is unknown"""
        return {
            "id": raw_data.get("id"),
            "data": raw_data,
            "summary": f"Generic data with {len(raw_data)} fields"
        }
    
    def aggregate_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple data points for reporting"""
        try:
            self.log_info(f"Aggregating {len(data_list)} data points")
            
            aggregated = {
                "total_records": len(data_list),
                "data_types": {},
                "summaries": [],
                "aggregated_at": datetime.utcnow().isoformat()
            }
            
            for data in data_list:
                data_type = data.get("data_type", "unknown")
                if data_type not in aggregated["data_types"]:
                    aggregated["data_types"][data_type] = 0
                aggregated["data_types"][data_type] += 1
                
                if "processed_data" in data and "summary" in data["processed_data"]:
                    aggregated["summaries"].append(data["processed_data"]["summary"])
            
            return aggregated
            
        except Exception as e:
            self.log_error(f"Error aggregating data: {str(e)}")
            raise
    
    def get_cached_data(self, data_type: str, data_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached processed data"""
        cache_key = f"processed:{data_type}:{data_hash}"
        return redis_client.get(cache_key)

# Global processor instance
processor = DataProcessor()
