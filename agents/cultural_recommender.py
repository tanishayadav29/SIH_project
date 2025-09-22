"""
Specialized cultural recommendations agent for Jharkhand tribal cultur
"""
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

def cultural_recommender(state):
    """Specialized cultural recommendations agent"""
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
    
    # Extract preferences
    preferences = state.get('preferences', {})
    month = preferences.get('month', 'October').lower()
    tribal_interest = preferences.get('tribal_interest', 'Medium')
    special_interests = preferences.get('special_interests', [])
    mobility_level = preferences.get('mobility_level', 'Moderate (Light walking)')
    budget_range = preferences.get('budget_range', 'Mid-Range (₹1500-3000/day)')
    
    # Get cultural data
    try:
        festivals = jharkhand_data.get_tribal_festivals_by_month(month)
        workshops = jharkhand_data.get_handicraft_workshops()
        homestays = jharkhand_data.get_homestay_options()
        guides = jharkhand_data.get_local_guides()
        etiquette = jharkhand_data.get_cultural_etiquette()
    except Exception as e:
        festivals = []
        workshops = []
        homestays = []
        guides = []
        etiquette = {}
    
    # Get filtered activities
    cultural_activities = get_cultural_activities_by_interest(tribal_interest, special_interests)
    interaction_guidelines = get_community_interaction_guidelines()
    
    prompt = f"""
You are a Jharkhand tribal culture specialist focused on authentic cultural experiences and community-based tourism.

**CULTURAL CONTEXT:**
- Month: {month.title()}
- Tribal Interest Level: {tribal_interest}
- Special Interests: {special_interests}
- Mobility Level: {mobility_level}
- Budget Range: {budget_range}

**RECOMMENDED CULTURAL ACTIVITIES (based on interest level):**
{json.dumps(cultural_activities, indent=2)}

**AVAILABLE TRIBAL FESTIVALS ({month}):**
{json.dumps([{{
    'name': f['name'],
    'description': f['description'],
    'activities': f['activities'],
    'best_locations': f['best_locations'],
    'visitor_experience': f['visitor_experience']
}} for f in festivals], indent=2)}

**AUTHENTIC WORKSHOPS:**
{json.dumps([{{
    'name': w['name'],
    'location': w['location'],
    'craft_type': w['craft_type'],
    'description': w['description'],
    'cost': w['cost'],
    'group_size': w['group_size']
}} for w in workshops], indent=2)}

**CULTURAL HOMESTAYS:**
{json.dumps([{{
    'name': h['name'],
    'community': h['community'],
    'description': h['description'],
    'special_features': h['special_features']
}} for h in homestays], indent=2)}

**COMMUNITY INTERACTION GUIDELINES:**
{json.dumps(interaction_guidelines, indent=2)}

**CULTURAL ETIQUETTE:**
{json.dumps(etiquette, indent=2)}

**INSTRUCTIONS:**
1. Focus on authentic tribal cultural experiences that match the interest level
2. Prioritize community-based tourism that benefits local communities
3. Include specific festivals and cultural events happening in {month}
4. Suggest workshops and hands-on cultural experiences
5. Recommend homestays for deeper cultural immersion
6. Provide detailed cultural context and significance
7. Include practical booking information and costs
8. Emphasize respectful cultural interaction
9. Suggest ways to support local artisans and communities
10. Include cultural etiquette reminders for each activity

**FORMAT:**
- Organize by cultural experience type (festivals, workshops, homestays, etc.)
- Include cultural significance and community impact
- Add practical details: timing, cost, booking requirements
- Provide cultural etiquette guidelines
- Include contact information and booking details
- Suggest optimal timing for cultural experiences

**CULTURAL SENSITIVITY FOCUS:**
- Emphasize respect for tribal traditions and customs
- Include guidance on appropriate behavior and dress
- Suggest ways to support local communities economically
- Provide context about cultural significance and history
- Include information about local languages and greetings
- Emphasize the importance of cultural preservation

Make recommendations that promote authentic cultural exchange while respecting and supporting Jharkhand's tribal communities.
"""
    
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"cultural_recommendations": result.strip()}
    except Exception as e:
        return {"cultural_recommendations": "", "warning": str(e)}
        