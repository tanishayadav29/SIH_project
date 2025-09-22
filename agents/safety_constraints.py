"""
Safety constraints and permit requirements agent for Jharkhand tourism
"""
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama
import json
import sys
import os

# Add data directory to path to import our data loader
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from data_loader import jharkhand_data

def load_safety_constraints():
    """Load safety constraints data"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'safety_constraints.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

def get_permit_requirements(destination, activity_type, safety_data):
    """Get permit requirements for specific destination and activity"""
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

def get_safety_guidelines(month, mobility_level, tourism_type, safety_data):
    """Get relevant safety guidelines based on context"""
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
    
    # Mobility level specific
    mobility_guidelines = safety_data.get('accessibility_constraints', {}).get('mobility_considerations', {})
    if mobility_level.lower().startswith('easy'):
        guidelines['mobility'] = mobility_guidelines.get('easy_mobility', {})
    elif mobility_level.lower().startswith('moderate'):
        guidelines['mobility'] = mobility_guidelines.get('moderate_mobility', {})
    elif mobility_level.lower().startswith('active'):
        guidelines['mobility'] = mobility_guidelines.get('active_mobility', {})
    elif mobility_level.lower().startswith('adventure'):
        guidelines['mobility'] = mobility_guidelines.get('adventure_mobility', {})
    
    return guidelines

def get_health_recommendations(month, safety_data):
    """Get health recommendations based on season"""
    health_data = safety_data.get('health_and_medical', {})
    recommendations = {}
    
    # Common health risks
    recommendations['risks'] = health_data.get('common_health_risks', {})
    
    # Medical facilities
    recommendations['facilities'] = health_data.get('medical_facilities', {})
    
    # Seasonal health considerations
    month_num = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }.get(month.lower(), 10)
    
    if month_num in [6, 7, 8, 9]:  # Monsoon
        recommendations['seasonal'] = {
            "waterborne_diseases": health_data.get('common_health_risks', {}).get('waterborne_diseases', {}),
            "mosquito_borne_diseases": health_data.get('common_health_risks', {}).get('mosquito_borne_diseases', {})
        }
    elif month_num in [3, 4, 5]:  # Summer
        recommendations['seasonal'] = {
            "heat_related_illnesses": health_data.get('common_health_risks', {}).get('heat_related_illnesses', {})
        }
    
    return recommendations

def safety_constraints_agent(state):
    """Safety constraints and permit requirements agent"""
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
    
    # Extract preferences
    preferences = state.get('preferences', {})
    destination = preferences.get('destination', 'Jharkhand')
    month = preferences.get('month', 'October').lower()
    tourism_type = preferences.get('tourism_type', 'Mixed Experience')
    mobility_level = preferences.get('mobility_level', 'Moderate (Light walking)')
    special_interests = preferences.get('special_interests', [])
    
    # Load safety constraints data
    safety_data = load_safety_constraints()
    
    # Get permit requirements
    permit_requirements = get_permit_requirements(destination, tourism_type, safety_data)
    
    # Get safety guidelines
    safety_guidelines = get_safety_guidelines(month, mobility_level, tourism_type, safety_data)
    
    # Get health recommendations
    health_recommendations = get_health_recommendations(month, safety_data)
    
    # Get seasonal constraints
    try:
        seasonal_constraints = jharkhand_data.get_seasonal_recommendations(month)
    except Exception as e:
        seasonal_constraints = {}
    
    prompt = f"""
You are a Jharkhand tourism safety specialist and permit requirements expert. Provide comprehensive safety guidance and permit information for travelers visiting Jharkhand.

**TRAVEL CONTEXT:**
- Destination: {destination}
- Month: {month.title()}
- Tourism Type: {tourism_type}
- Mobility Level: {mobility_level}
- Special Interests: {special_interests}

**PERMIT REQUIREMENTS:**
{json.dumps(permit_requirements, indent=2)}

**SAFETY GUIDELINES:**
{json.dumps(safety_guidelines, indent=2)}

**HEALTH RECOMMENDATIONS:**
{json.dumps(health_recommendations, indent=2)}

**SEASONAL CONSTRAINTS:**
{json.dumps(seasonal_constraints, indent=2)}

**INSTRUCTIONS:**
1. Provide detailed permit requirements for the destination and activities
2. Include comprehensive safety guidelines based on season and mobility level
3. Give specific health recommendations for the travel month
4. Include emergency contact information and procedures
5. Provide accessibility considerations based on mobility level
6. Include cultural safety guidelines for tribal areas
7. Suggest insurance requirements and recommendations
8. Include seasonal safety precautions
9. Provide practical safety tips and precautions
10. Include emergency procedures and contact information

**FORMAT:**
- Permit Requirements and Booking Information
- General Safety Guidelines
- Seasonal Safety Precautions
- Health Recommendations and Medical Facilities
- Emergency Contacts and Procedures
- Accessibility Considerations
- Cultural Safety Guidelines
- Insurance Recommendations
- Practical Safety Tips

**SAFETY EMPHASIS:**
- Prioritize traveler safety and well-being
- Include specific precautions for Jharkhand's unique conditions
- Provide clear emergency procedures
- Emphasize respect for local communities and environment
- Include practical, actionable safety advice

Make the safety guidance comprehensive, practical, and focused on ensuring safe and respectful travel in Jharkhand.
"""
    
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"safety_constraints": result.strip()}
    except Exception as e:
        return {"safety_constraints": "", "warning": str(e)}