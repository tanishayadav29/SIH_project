from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama
import json
import sys
import os

# Add data directory to path to import our data loader
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from data_loader import jharkhand_data

def get_cultural_activities_by_interest(tribal_interest, special_interests):
    """Filter cultural activities based on interest level and special interests"""
    activities = []
    
    if tribal_interest in ["High", "Very High"]:
        activities.extend([
            "Tribal village homestays",
            "Traditional music and dance performances", 
            "Cultural storytelling sessions",
            "Traditional medicine workshops",
            "Sacred grove visits",
            "Community-based tourism activities"
        ])
    
    if tribal_interest in ["Medium", "High", "Very High"]:
        activities.extend([
            "Handicraft workshops",
            "Local market visits",
            "Cultural museum visits",
            "Traditional cooking classes"
        ])
    
    # Add activities based on special interests
    if "Tribal festivals & ceremonies" in special_interests:
        activities.append("Tribal festival participation")
    if "Handicraft workshops" in special_interests:
        activities.append("Artisan workshop visits")
    if "Traditional music & dance" in special_interests:
        activities.append("Traditional performance attendance")
    if "Local cuisine & cooking" in special_interests:
        activities.append("Traditional cooking experiences")
    
    return list(set(activities))  # Remove duplicates

def get_community_interaction_guidelines():
    """Get guidelines for respectful community interaction"""
    return {
        "before_visit": [
            "Learn basic greetings in local languages",
            "Research cultural customs and traditions",
            "Bring small gifts for host families",
            "Dress modestly and appropriately"
        ],
        "during_visit": [
            "Ask permission before photographing people",
            "Participate respectfully in ceremonies",
            "Support local artisans by purchasing handicrafts",
            "Follow local customs and traditions"
        ],
        "after_visit": [
            "Share positive experiences respectfully",
            "Support community initiatives",
            "Maintain respectful relationships"
        ]
    }

def recommend_activities(state):
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
    
    # Extract preferences
    preferences = state.get('preferences', {})
    month = preferences.get('month', 'October').lower()
    tourism_type = preferences.get('tourism_type', 'Mixed Experience')
    tribal_interest = preferences.get('tribal_interest', 'Medium')
    special_interests = preferences.get('special_interests', [])
    mobility_level = preferences.get('mobility_level', 'Moderate (Light walking)')
    budget_range = preferences.get('budget_range', 'Mid-Range (₹1500-3000/day)')
    itinerary = state.get('itinerary', '')
    
    # Get Jharkhand-specific cultural data
    try:
        # Get tribal festivals for the month
        festivals = jharkhand_data.get_tribal_festivals_by_month(month)
        
        # Get handicraft workshops
        workshops = jharkhand_data.get_handicraft_workshops()
        
        # Get homestay options
        homestays = jharkhand_data.get_homestay_options()
        
        # Get local guides
        guides = jharkhand_data.get_local_guides()
        
        # Get cultural etiquette
        etiquette = jharkhand_data.get_cultural_etiquette()
        
        # Get POIs for cultural activities
        cultural_pois = jharkhand_data.get_pois_by_category('cultural')
        
        # Get filtered cultural activities based on interest
        cultural_activities = get_cultural_activities_by_interest(tribal_interest, special_interests)
        
        # Get community interaction guidelines
        interaction_guidelines = get_community_interaction_guidelines()
        
    except Exception as e:
        # Fallback to basic data if loading fails
        festivals = []
        workshops = []
        homestays = []
        guides = []
        etiquette = {}
        cultural_pois = []
        cultural_activities = []
        interaction_guidelines = {}
    
    # Create comprehensive cultural activities prompt
    prompt = f"""
You are a Jharkhand eco-cultural tourism specialist and activities expert. Based on the user's preferences and itinerary, suggest authentic activities that balance cultural experiences with nature, adventure, and spiritual tourism.

**USER PREFERENCES:**
{json.dumps(preferences, indent=2)}

**CURRENT ITINERARY:**
{itinerary}

**TOURISM CONTEXT:**
- Month: {month.title()}
- Tourism Type: {tourism_type}
- Tribal Interest Level: {tribal_interest}
- Mobility Level: {mobility_level}
- Budget Range: {budget_range}
- Special Interests: {special_interests}

**RECOMMENDED CULTURAL ACTIVITIES (based on interest level):**
{json.dumps(cultural_activities, indent=2)}

**AVAILABLE TRIBAL FESTIVALS ({month}):**
{json.dumps([{
    'name': f['name'],
    'description': f['description'],
    'activities': f['activities'],
    'best_locations': f['best_locations'],
    'duration': f['duration'],
    'visitor_experience': f['visitor_experience']
} for f in festivals], indent=2)}

**HANDICRAFT WORKSHOPS:**
{json.dumps([{
    'name': w['name'],
    'location': w['location'],
    'craft_type': w['craft_type'],
    'description': w['description'],
    'duration': w['duration'],
    'cost': w['cost'],
    'group_size': w['group_size'],
    'season': w['season']
} for w in workshops], indent=2)}

**CULTURAL HOMESTAYS:**
{json.dumps([{
    'name': h['name'],
    'location': h['location'],
    'community': h['community'],
    'description': h['description'],
    'amenities': h['amenities'],
    'special_features': h['special_features']
} for h in homestays], indent=2)}

**LOCAL GUIDES:**
{json.dumps([{
    'name': g['name'],
    'specialization': g['specialization'],
    'languages': g['languages'],
    'services': g['services'],
    'cost_per_day': g['cost_per_day']
} for g in guides], indent=2)}

**COMMUNITY INTERACTION GUIDELINES:**
{json.dumps(interaction_guidelines, indent=2)}

**CULTURAL ETIQUETTE:**
{json.dumps(etiquette, indent=2)}

**INSTRUCTIONS:**
1. Suggest activities that match the user's tourism_type and tribal_interest level
2. Include festivals, workshops, and cultural experiences available during {month}
3. Consider mobility_level when suggesting activities
4. Incorporate special_interests into recommendations
5. Provide cultural context and significance for each activity
6. Include practical information: timing, cost in INR, booking requirements
7. Suggest ways to respectfully engage with tribal communities
8. Include cultural etiquette reminders for each activity
9. Balance cultural experiences with nature, adventure, and spiritual activities
10. Provide contact information and booking details where available
11. Consider budget_range when suggesting activities
12. Organize suggestions by day if itinerary is provided
13. Include both popular attractions and authentic local experiences
14. Suggest optimal timing for different types of activities

**ACTIVITY CATEGORIES TO CONSIDER:**
**Cultural & Tribal:**
- Tribal festivals and ceremonies
- Handicraft workshops and artisan visits
- Cultural homestay experiences
- Traditional music and dance performances
- Cultural storytelling sessions
- Traditional cooking classes
- Village walks and community interactions
- Cultural museum visits
- Traditional medicine workshops
- Sacred grove visits

**Nature & Adventure:**
- Wildlife safaris and national park visits
- Trekking and hiking trails
- Waterfall visits and nature photography
- Bird watching and nature walks
- Adventure activities (based on mobility level)

**Spiritual & Religious:**
- Temple visits and pilgrimage sites
- Spiritual experiences and meditation
- Religious ceremonies and rituals

**Local Experiences:**
- Local market visits and artisan shopping
- Community-based tourism activities
- Local cuisine experiences
- Traditional craft demonstrations

**FORMAT:**
- Organize suggestions by day if itinerary is provided
- Include activity name, description, and cultural significance
- Add practical details: timing, cost, duration, group size
- Include cultural etiquette reminders
- Provide booking information and contact details
- Suggest optimal timing for cultural experiences
- Include transportation and accessibility information

**CULTURAL SENSITIVITY:**
- Always emphasize respect for tribal traditions
- Include guidance on appropriate behavior
- Suggest ways to support local communities
- Provide context about cultural significance
- Include information about local customs and practices

Make the suggestions authentic, respectful, and focused on meaningful cultural exchange with Jharkhand's tribal communities.
"""
    
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"activity_suggestions": result.strip()}
    except Exception as e:
        return {"activity_suggestions": "", "warning": str(e)}