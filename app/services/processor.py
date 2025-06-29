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
            elif data_type == "company":
                processed_data["processed_data"] = self._process_company_data(raw_data)
            elif data_type == "farm":
                processed_data["processed_data"] = self._process_farm_data(raw_data)
            elif data_type == "season":
                processed_data["processed_data"] = self._process_season_data(raw_data)
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
            "farm_id": raw_data.get("farm_id"),
            "description": raw_data.get("description"),
            "cropping_method": raw_data.get("cropping_method"),
            "crops": raw_data.get("crops", []),
            "chemical_cost": raw_data.get("chemical_cost"),
            "fertilizer_cost": raw_data.get("fertilizer_cost"),
            "seed_cost": raw_data.get("seed_cost"),
            "summary": f"Field: {raw_data.get('name', 'Unknown')} - Area: {raw_data.get('area', 'N/A')} - Farm: {raw_data.get('farm_id', 'N/A')}"
        }
    
    def _process_crop_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process crop-specific data"""
        return {
            "crop_id": raw_data.get("id"),
            "crop_type": raw_data.get("type"),
            "variety": raw_data.get("variety"),
            "field_id": raw_data.get("field_id"),
            "crop_grade": raw_data.get("crop_grade"),
            "crop_use": raw_data.get("crop_use"),
            "crop_blend": raw_data.get("crop_blend"),
            "planting_date": raw_data.get("planting_date"),
            "harvest_date": raw_data.get("harvest_date"),
            "summary": f"Crop: {raw_data.get('type', 'Unknown')} - Variety: {raw_data.get('variety', 'N/A')} - Field: {raw_data.get('field_id', 'N/A')}"
        }
    
    def _process_activity_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity-specific data"""
        return {
            "activity_id": raw_data.get("id"),
            "title": raw_data.get("title"),
            "activity_type": raw_data.get("activity_type"),
            "activity_category": raw_data.get("activity_category"),
            "approved": raw_data.get("approved"),
            "completed": raw_data.get("completed"),
            "area": raw_data.get("area"),
            "total_cost": raw_data.get("total_cost"),
            "chemical_cost": raw_data.get("chemical_cost"),
            "fertilizer_cost": raw_data.get("fertilizer_cost"),
            "seed_cost": raw_data.get("seed_cost"),
            "due_at": raw_data.get("due_at"),
            "completed_at": raw_data.get("completed_at"),
            "company_name": raw_data.get("company_name"),
            "author_user_name": raw_data.get("author_user_name"),
            "activity_fields": raw_data.get("activity_fields", []),
            "activity_inputs": raw_data.get("activity_inputs", []),
            "summary": f"Activity: {raw_data.get('title', 'Unknown')} - Type: {raw_data.get('activity_type', 'N/A')} - Status: {'Completed' if raw_data.get('completed') else 'Pending'}"
        }
    
    def _process_generic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic data when type is unknown"""
        return {
            "id": raw_data.get("id"),
            "data": raw_data,
            "summary": f"Generic data with {len(raw_data)} fields"
        }
    
    def _process_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process company-specific data"""
        return {
            "company_id": raw_data.get("id"),
            "company_name": raw_data.get("name"),
            "company_type": raw_data.get("company_type"),
            "business_identifier": raw_data.get("business_identifier"),
            "contact_email": raw_data.get("contact_email"),
            "contact_name": raw_data.get("contact_name"),
            "description": raw_data.get("description"),
            "physical_location": raw_data.get("physical_location"),
            "summary": f"Company: {raw_data.get('name', 'Unknown')} - Type: {raw_data.get('company_type', 'N/A')}"
        }
    
    def _process_farm_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process farm-specific data"""
        return {
            "farm_id": raw_data.get("id"),
            "farm_name": raw_data.get("name"),
            "company_id": raw_data.get("company_id"),
            "description": raw_data.get("description"),
            "location": raw_data.get("location"),
            "reporting_region": raw_data.get("reporting_region"),
            "summary": f"Farm: {raw_data.get('name', 'Unknown')} - Region: {raw_data.get('reporting_region', 'N/A')}"
        }
    
    def _process_season_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process season-specific data"""
        return {
            "season_id": raw_data.get("id"),
            "season_name": raw_data.get("name"),
            "company_id": raw_data.get("company_id"),
            "approved": raw_data.get("approved"),
            "season_start_date": raw_data.get("season_start_date"),
            "season_end_date": raw_data.get("season_end_date"),
            "summary": f"Season: {raw_data.get('name', 'Unknown')} - Status: {'Approved' if raw_data.get('approved') else 'Draft'}"
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
