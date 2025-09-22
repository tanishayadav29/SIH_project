"""
Data loader utility for Jharkhand tourism data
"""
import json
import os
from typing import Dict, List, Optional, Any

class JharkhandDataLoader:
    """Utility class to load and manage Jharkhand tourism data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._pois_data = None
        self._tribal_data = None
        self._seasonal_data = None
        self._cuisine_data = None
        self._safety_data = None
    
    def load_pois(self) -> Dict[str, Any]:
        """Load Points of Interest data"""
        if self._pois_data is None:
            file_path = os.path.join(self.data_dir, "jharkhand_pois.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self._pois_data = json.load(f)
        return self._pois_data
    
    def load_tribal_culture(self) -> Dict[str, Any]:
        """Load tribal culture data"""
        if self._tribal_data is None:
            file_path = os.path.join(self.data_dir, "tribal_culture_data.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self._tribal_data = json.load(f)
        return self._tribal_data
    
    def load_seasonal_constraints(self) -> Dict[str, Any]:
        """Load seasonal constraints data"""
        if self._seasonal_data is None:
            file_path = os.path.join(self.data_dir, "seasonal_constraints.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self._seasonal_data = json.load(f)
        return self._seasonal_data
    
    def load_cuisine_data(self) -> Dict[str, Any]:
        """Load Jharkhand cuisine data"""
        if self._cuisine_data is None:
            file_path = os.path.join(self.data_dir, "jharkhand_cuisine.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self._cuisine_data = json.load(f)
        return self._cuisine_data
    
    def load_safety_constraints(self) -> Dict[str, Any]:
        """Load safety constraints data"""
        if self._safety_data is None:
            file_path = os.path.join(self.data_dir, "safety_constraints.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                self._safety_data = json.load(f)
        return self._safety_data
    
    def get_pois_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get POIs filtered by category"""
        pois_data = self.load_pois()
        return [poi for poi in pois_data['pois'] if poi['category'] == category]
    
    def get_pois_by_season(self, month: str) -> List[Dict[str, Any]]:
        """Get POIs suitable for a specific month"""
        pois_data = self.load_pois()
        seasonal_data = self.load_seasonal_constraints()
        
        # Get season for the month
        season = None
        for season_name, season_info in seasonal_data['seasons'].items():
            if month.lower() in season_info['months']:
                season = season_name
                break
        
        if not season:
            return pois_data['pois']  # Return all if season not found
        
        suitable_pois = []
        for poi in pois_data['pois']:
            if month.lower() in poi['best_season']:
                suitable_pois.append(poi)
        
        return suitable_pois
    
    def get_poi_by_id(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific POI by ID"""
        pois_data = self.load_pois()
        for poi in pois_data['pois']:
            if poi['id'] == poi_id:
                return poi
        return None
    
    def get_tribal_festivals_by_month(self, month: str) -> List[Dict[str, Any]]:
        """Get tribal festivals for a specific month"""
        tribal_data = self.load_tribal_culture()
        festivals = []
        for festival in tribal_data['cultural_festivals']:
            if month.lower() in festival['month'].lower():
                festivals.append(festival)
        return festivals
    
    def get_handicraft_workshops(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get handicraft workshops, optionally filtered by location"""
        tribal_data = self.load_tribal_culture()
        workshops = tribal_data['handicraft_workshops']
        
        if location:
            workshops = [w for w in workshops if location.lower() in w['location'].lower()]
        
        return workshops
    
    def get_homestay_options(self, community: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get homestay options, optionally filtered by tribal community"""
        tribal_data = self.load_tribal_culture()
        homestays = tribal_data['homestay_options']
        
        if community:
            homestays = [h for h in homestays if community.lower() in h['community'].lower()]
        
        return homestays
    
    def get_seasonal_recommendations(self, month: str) -> Dict[str, Any]:
        """Get seasonal recommendations for a specific month"""
        seasonal_data = self.load_seasonal_constraints()
        return seasonal_data['monthly_recommendations'].get(month.lower(), {})
    
    def get_accessibility_info(self, attraction_type: str, month: str) -> str:
        """Get accessibility information for an attraction type in a specific month"""
        seasonal_data = self.load_seasonal_constraints()
        
        # Determine season
        season = None
        for season_name, season_info in seasonal_data['seasons'].items():
            if month.lower() in season_info['months']:
                season = season_name
                break
        
        if not season:
            return "Unknown"
        
        accessibility_matrix = seasonal_data['accessibility_matrix']
        return accessibility_matrix.get(attraction_type, {}).get(season, "Unknown")
    
    def search_pois(self, query: str) -> List[Dict[str, Any]]:
        """Search POIs by name, description, or activities"""
        pois_data = self.load_pois()
        query_lower = query.lower()
        
        matching_pois = []
        for poi in pois_data['pois']:
            # Search in name, description, and activities
            if (query_lower in poi['name'].lower() or 
                query_lower in poi['description'].lower() or
                any(query_lower in activity.lower() for activity in poi['activities'])):
                matching_pois.append(poi)
        
        return matching_pois
    
    def get_cultural_etiquette(self) -> Dict[str, List[str]]:
        """Get cultural etiquette guidelines"""
        tribal_data = self.load_tribal_culture()
        return tribal_data['cultural_etiquette']
    
    def get_local_guides(self, specialization: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get local guides, optionally filtered by specialization"""
        tribal_data = self.load_tribal_culture()
        guides = tribal_data['local_guides']
        
        if specialization:
            guides = [g for g in guides if specialization.lower() in g['specialization'].lower()]
        
        return guides
    
    def get_traditional_dishes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get traditional dishes, optionally filtered by category"""
        cuisine_data = self.load_cuisine_data()
        dishes = cuisine_data.get('traditional_dishes', [])
        
        if category:
            dishes = [d for d in dishes if d['category'] == category]
        
        return dishes
    
    def get_cooking_experiences(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get cooking experiences, optionally filtered by location"""
        cuisine_data = self.load_cuisine_data()
        experiences = cuisine_data.get('cooking_experiences', [])
        
        if location:
            experiences = [e for e in experiences if location.lower() in e['location'].lower()]
        
        return experiences
    
    def get_food_markets(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get food markets, optionally filtered by location"""
        cuisine_data = self.load_cuisine_data()
        markets = cuisine_data.get('food_markets', [])
        
        if location:
            markets = [m for m in markets if location.lower() in m['location'].lower()]
        
        return markets
    
    def get_permit_requirements(self, destination: str, activity_type: str = "") -> Dict[str, Any]:
        """Get permit requirements for specific destination and activity"""
        safety_data = self.load_safety_constraints()
        permit_data = safety_data.get('permit_requirements', {})
        
        # Check national parks
        if 'national park' in destination.lower() or 'betla' in destination.lower():
            return permit_data.get('national_parks', {}).get('betla_national_park', {})
        elif 'hazaribagh' in destination.lower():
            return permit_data.get('national_parks', {}).get('hazaribagh_national_park', {})
        
        # Check wildlife sanctuaries
        if 'wildlife' in activity_type.lower() or 'safari' in activity_type.lower():
            return permit_data.get('wildlife_sanctuaries', {}).get('dalma_wildlife_sanctuary', {})
        
        # Check tribal areas
        if 'tribal' in activity_type.lower() or 'village' in destination.lower():
            return permit_data.get('tribal_areas', {}).get('village_visits', {})
        
        return {}
    
    def get_safety_guidelines(self, month: str, mobility_level: str = "", tourism_type: str = "") -> Dict[str, Any]:
        """Get safety guidelines based on context"""
        safety_data = self.load_safety_constraints()
        guidelines = {}
        
        # General safety
        guidelines['general'] = safety_data.get('safety_guidelines', {}).get('general_safety', {})
        
        # Seasonal safety
        month_num = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }.get(month.lower(), 10)
        
        if month_num in [6, 7, 8, 9]:  # Monsoon
            guidelines['seasonal'] = safety_data.get('safety_guidelines', {}).get('monsoon_safety', {})
        elif month_num in [3, 4, 5]:  # Summer
            guidelines['seasonal'] = safety_data.get('seasonal_constraints', {}).get('summer_precautions', {})
        elif month_num in [12, 1, 2]:  # Winter
            guidelines['seasonal'] = safety_data.get('seasonal_constraints', {}).get('winter_considerations', {})
        
        # Tourism type specific
        if 'wildlife' in tourism_type.lower() or 'adventure' in tourism_type.lower():
            guidelines['wildlife'] = safety_data.get('safety_guidelines', {}).get('wildlife_safety', {})
        
        if 'cultural' in tourism_type.lower() or 'tribal' in tourism_type.lower():
            guidelines['cultural'] = safety_data.get('safety_guidelines', {}).get('cultural_safety', {})
        
        return guidelines
    
    def get_emergency_contacts(self) -> Dict[str, Any]:
        """Get emergency contact information"""
        safety_data = self.load_safety_constraints()
        return safety_data.get('safety_guidelines', {}).get('general_safety', {}).get('emergency_contacts', {})

# Global instance for easy access
jharkhand_data = JharkhandDataLoader()