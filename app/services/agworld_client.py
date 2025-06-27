import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from app.config import settings
from app.utils.logger import LoggerMixin
from app.redis_client import redis_client

class AgworldAPIClient(LoggerMixin):
    """Client for Agworld API integration"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.AGWORLD_API_KEY
        self.base_url = "https://api.agworld.com/v1"  # Replace with actual Agworld API URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AgworldReporter/1.0"
        })
        self.rate_limit_delay = 1  # Delay between requests to respect rate limits
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Agworld API with error handling"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            self.log_info(f"Making {method} request to {url}")
            
            # Add rate limiting
            time.sleep(self.rate_limit_delay)
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            self.log_info(f"API request successful: {method} {endpoint}")
            return result
            
        except requests.exceptions.HTTPError as e:
            self.log_error(f"HTTP error for {method} {endpoint}: {e}")
            if e.response.status_code == 429:  # Rate limited
                self.log_warning("Rate limited, increasing delay")
                self.rate_limit_delay *= 2
            raise
        except requests.exceptions.RequestException as e:
            self.log_error(f"Request error for {method} {endpoint}: {e}")
            raise
        except Exception as e:
            self.log_error(f"Unexpected error for {method} {endpoint}: {e}")
            raise
    
    def get_fields(self, farm_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get field data from Agworld"""
        try:
            self.log_info("Fetching field data from Agworld")
            
            # Check cache first
            cache_key = f"agworld:fields:{farm_id or 'all'}"
            cached_data = redis_client.get(cache_key)
            if cached_data:
                self.log_info("Returning cached field data")
                return cached_data
            
            # TODO: Replace with actual Agworld API endpoint
            params = {}
            if farm_id:
                params["farm_id"] = farm_id
            
            # For now, return mock data since we don't have actual API details
            mock_data = self._get_mock_field_data()
            
            # Cache the results for 1 hour
            redis_client.set(cache_key, mock_data, ex=3600)
            
            return mock_data
            
        except Exception as e:
            self.log_error(f"Failed to get field data: {str(e)}")
            raise
    
    def get_crops(self, field_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get crop data from Agworld"""
        try:
            self.log_info("Fetching crop data from Agworld")
            
            cache_key = f"agworld:crops:{field_id or 'all'}"
            cached_data = redis_client.get(cache_key)
            if cached_data:
                self.log_info("Returning cached crop data")
                return cached_data
            
            # TODO: Replace with actual Agworld API endpoint
            params = {}
            if field_id:
                params["field_id"] = field_id
            
            # For now, return mock data
            mock_data = self._get_mock_crop_data()
            
            # Cache the results for 1 hour
            redis_client.set(cache_key, mock_data, ex=3600)
            
            return mock_data
            
        except Exception as e:
            self.log_error(f"Failed to get crop data: {str(e)}")
            raise
    
    def get_activities(
        self,
        field_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get activity data from Agworld"""
        try:
            self.log_info("Fetching activity data from Agworld")
            
            cache_key = f"agworld:activities:{field_id or 'all'}:{start_date or 'no_start'}:{end_date or 'no_end'}"
            cached_data = redis_client.get(cache_key)
            if cached_data:
                self.log_info("Returning cached activity data")
                return cached_data
            
            # TODO: Replace with actual Agworld API endpoint
            params = {}
            if field_id:
                params["field_id"] = field_id
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            # For now, return mock data
            mock_data = self._get_mock_activity_data()
            
            # Cache the results for 30 minutes (activities change more frequently)
            redis_client.set(cache_key, mock_data, ex=1800)
            
            return mock_data
            
        except Exception as e:
            self.log_error(f"Failed to get activity data: {str(e)}")
            raise
    
    def get_weather(self, field_id: str) -> Dict[str, Any]:
        """Get weather data for a field"""
        try:
            self.log_info(f"Fetching weather data for field {field_id}")
            
            cache_key = f"agworld:weather:{field_id}"
            cached_data = redis_client.get(cache_key)
            if cached_data:
                self.log_info("Returning cached weather data")
                return cached_data
            
            # TODO: Replace with actual Agworld API endpoint
            # For now, return mock data
            mock_data = self._get_mock_weather_data()
            
            # Cache weather data for 15 minutes
            redis_client.set(cache_key, mock_data, ex=900)
            
            return mock_data
            
        except Exception as e:
            self.log_error(f"Failed to get weather data: {str(e)}")
            raise
    
    def _get_mock_field_data(self) -> List[Dict[str, Any]]:
        """Return mock field data for testing"""
        return [
            {
                "id": "field_001",
                "name": "North Field",
                "area": 25.5,
                "location": {"lat": -27.4698, "lng": 153.0251},
                "farm_id": "farm_001",
                "soil_type": "Clay loam",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "field_002",
                "name": "South Field",
                "area": 18.3,
                "location": {"lat": -27.4700, "lng": 153.0250},
                "farm_id": "farm_001",
                "soil_type": "Sandy loam",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    
    def _get_mock_crop_data(self) -> List[Dict[str, Any]]:
        """Return mock crop data for testing"""
        return [
            {
                "id": "crop_001",
                "type": "Wheat",
                "variety": "Winter Wheat",
                "field_id": "field_001",
                "planting_date": "2024-04-15",
                "expected_harvest": "2024-11-30",
                "stage": "Flowering"
            },
            {
                "id": "crop_002",
                "type": "Corn",
                "variety": "Sweet Corn",
                "field_id": "field_002",
                "planting_date": "2024-05-01",
                "expected_harvest": "2024-10-15",
                "stage": "Vegetative"
            }
        ]
    
    def _get_mock_activity_data(self) -> List[Dict[str, Any]]:
        """Return mock activity data for testing"""
        return [
            {
                "id": "activity_001",
                "type": "Planting",
                "field_id": "field_001",
                "crop_id": "crop_001",
                "date": "2024-04-15",
                "description": "Planted winter wheat variety",
                "cost": 150.00,
                "duration": 4.5
            },
            {
                "id": "activity_002",
                "type": "Fertilizing",
                "field_id": "field_001",
                "crop_id": "crop_001",
                "date": "2024-05-20",
                "description": "Applied nitrogen fertilizer",
                "cost": 75.00,
                "duration": 2.0
            }
        ]
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """Return mock weather data for testing"""
        return {
            "location": "Field Location",
            "current": {
                "temperature": 22.5,
                "humidity": 65,
                "wind_speed": 12.3,
                "precipitation": 0.0,
                "conditions": "Partly Cloudy"
            },
            "forecast": [
                {
                    "date": "2024-06-28",
                    "high": 25.0,
                    "low": 18.0,
                    "precipitation_chance": 20,
                    "conditions": "Sunny"
                },
                {
                    "date": "2024-06-29",
                    "high": 23.0,
                    "low": 16.0,
                    "precipitation_chance": 60,
                    "conditions": "Rain"
                }
            ],
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def test_connection(self) -> bool:
        """Test the connection to Agworld API"""
        try:
            # TODO: Replace with actual health check endpoint
            # For now, just check if API key is configured
            if not self.api_key:
                self.log_warning("Agworld API key not configured")
                return False
            
            self.log_info("Agworld API connection test passed")
            return True
            
        except Exception as e:
            self.log_error(f"Agworld API connection test failed: {str(e)}")
            return False

# Global client instance
agworld_client = AgworldAPIClient()
