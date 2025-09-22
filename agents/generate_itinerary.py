from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama
import json
import sys
import os

# Add data directory to path to import our data loader
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from data_loader import jharkhand_data

def get_tourism_focus_pois(tourism_type, suitable_pois):
    """Filter POIs based on tourism type preference"""
    if tourism_type == "Eco-Tourism & Nature":
        return [poi for poi in suitable_pois if poi['category'] == 'nature']
    elif tourism_type == "Tribal Culture & Heritage":
        return [poi for poi in suitable_pois if poi['category'] == 'cultural'] + \
               [poi for poi in suitable_pois if 'tribal' in poi['description'].lower()]
    elif tourism_type == "Pilgrimage & Spiritual":
        return [poi for poi in suitable_pois if poi['category'] == 'religious']
    elif tourism_type == "Adventure & Trekking":
        return [poi for poi in suitable_pois if poi['difficulty_level'] in ['moderate', 'challenging']]
    elif tourism_type == "Photography & Wildlife":
        return [poi for poi in suitable_pois if 'photography' in poi['activities'] or poi['category'] == 'nature']
    else:  # Mixed Experience
        return suitable_pois

def get_accommodation_suggestions(accommodation_type, budget_range):
    """Get accommodation suggestions based on preferences"""
    suggestions = []
    
    if "Homestays" in accommodation_type:
        suggestions.append("🏠 Tribal village homestays for authentic cultural immersion")
    if "Eco-lodges" in accommodation_type:
        suggestions.append("🌿 Eco-lodges near national parks and nature reserves")
    if "Hotels" in accommodation_type:
        suggestions.append("🏨 Comfortable hotels in major cities like Ranchi and Deoghar")
    
    # Add budget context
    if "Budget" in budget_range:
        suggestions.append("💰 Budget-friendly options: ₹500-1500/day")
    elif "Mid-Range" in budget_range:
        suggestions.append("💰 Mid-range options: ₹1500-3000/day")
    elif "Comfortable" in budget_range:
        suggestions.append("💰 Comfortable options: ₹3000-5000/day")
    elif "Luxury" in budget_range:
        suggestions.append("💰 Luxury options: ₹5000+/day")
    
    return suggestions

def generate_itinerary(state):
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
    
    # Extract preferences
    preferences = state.get('preferences', {})
    month = preferences.get('month', 'October').lower()
    duration = preferences.get('duration', 7)
    tourism_type = preferences.get('tourism_type', 'Mixed Experience')
    tribal_interest = preferences.get('tribal_interest', 'Medium')
    mobility_level = preferences.get('mobility_level', 'Moderate (Light walking)')
    accommodation_type = preferences.get('accommodation_type', 'Mixed (Homestays + Hotels)')
    budget_range = preferences.get('budget_range', 'Mid-Range (₹1500-3000/day)')
    special_interests = preferences.get('special_interests', [])
    
    # Get Jharkhand-specific data
    try:
        # Get suitable POIs for the month
        suitable_pois = jharkhand_data.get_pois_by_season(month)
        
        # Filter POIs based on tourism type
        focused_pois = get_tourism_focus_pois(tourism_type, suitable_pois)
        
        # Get seasonal recommendations
        seasonal_info = jharkhand_data.get_seasonal_recommendations(month)
        
        # Get tribal festivals for the month
        festivals = jharkhand_data.get_tribal_festivals_by_month(month)
        
        # Get handicraft workshops
        workshops = jharkhand_data.get_handicraft_workshops()
        
        # Get homestay options
        homestays = jharkhand_data.get_homestay_options()
        
        # Get cultural etiquette
        etiquette = jharkhand_data.get_cultural_etiquette()
        
        # Get accommodation suggestions
        accommodation_suggestions = get_accommodation_suggestions(accommodation_type, budget_range)
        
    except Exception as e:
        # Fallback to basic data if loading fails
        focused_pois = []
        seasonal_info = {}
        festivals = []
        workshops = []
        homestays = []
        etiquette = {}
        accommodation_suggestions = []
    
    # Create comprehensive prompt with Jharkhand context
    prompt = f"""
You are an expert Jharkhand eco-cultural tourism specialist. Create a detailed, culturally-sensitive itinerary for Jharkhand based on the following preferences:

**TRAVEL PREFERENCES:**
{json.dumps(preferences, indent=2)}

**JHARKHAND CONTEXT:**
- Month: {month.title()}
- Duration: {duration} days
- Tourism Focus: {tourism_type}
- Tribal Culture Interest: {tribal_interest}
- Mobility Level: {mobility_level}
- Accommodation: {accommodation_type}
- Budget: {budget_range}

**SEASONAL INFORMATION:**
{json.dumps(seasonal_info, indent=2)}

**AVAILABLE DESTINATIONS (focused on {tourism_type} for {month}):**
{json.dumps([
    {
        'name': poi['name'],
        'category': poi['category'],
        'description': poi['description'],
        'activities': poi['activities'],
        'duration_recommended': poi['duration_recommended'],
        'difficulty_level': poi['difficulty_level'],
        'entry_fee': poi['entry_fee'],
        'special_notes': poi['special_notes'],
        'cultural_significance': poi.get('cultural_significance', ''),
        'safety_notes': poi.get('safety_notes', '')
    }
    for poi in focused_pois[:8]
], indent=2)}

**TRIBAL CULTURAL OPPORTUNITIES:**
Festivals: {json.dumps([f['name'] for f in festivals], indent=2)}
Workshops: {json.dumps([w['name'] + ' (' + w['location'] + ')' for w in workshops[:3]], indent=2)}
Homestays: {json.dumps([h['name'] + ' (' + h['community'] + ')' for h in homestays[:2]], indent=2)}

**ACCOMMODATION SUGGESTIONS:**
{json.dumps(accommodation_suggestions, indent=2)}

**CULTURAL ETIQUETTE GUIDELINES:**
{json.dumps(etiquette, indent=2)}

**SPECIAL INTERESTS TO INCORPORATE:**
{json.dumps(special_interests, indent=2)}

**INSTRUCTIONS:**
1. Create a day-by-day itinerary focusing on Jharkhand's eco-cultural tourism
2. Prioritize destinations based on tourism_type and tribal_interest level
3. Respect seasonal constraints and accessibility (monsoon considerations)
4. Include cultural experiences appropriate for the tribal_interest level
5. Suggest accommodation based on accommodation_type preference
6. Include practical information: travel times, entry fees, safety notes
7. Add cultural etiquette reminders where relevant
8. Balance popular attractions with authentic local experiences
9. Include downtime and cultural immersion opportunities
10. Provide budget-conscious suggestions in INR
11. Incorporate special interests from the user's preferences
12. Consider mobility level for activity recommendations
13. Include local transportation options and costs
14. Add cultural context and significance for each destination
15. Suggest optimal timing for cultural experiences and festivals

**FORMAT:**
- Day-by-day breakdown with specific timings (morning, afternoon, evening)
- Include travel time between locations and transportation options
- Mention cultural significance and tribal heritage of each site
- Add practical tips, safety considerations, and entry fees in INR
- Include specific accommodation suggestions with contact information
- Add cultural etiquette reminders and respectful behavior guidelines
- Include local food recommendations and cultural dining experiences
- Suggest photography opportunities and cultural interaction guidelines
- Add weather considerations and seasonal advice
- Include budget breakdown and cost-saving tips

**CULTURAL SENSITIVITY:**
- Always emphasize respect for tribal communities and their traditions
- Include guidance on appropriate behavior in sacred spaces
- Suggest ways to support local artisans and communities
- Provide context about the cultural significance of each experience
- Include information about local languages and basic greetings

Make the itinerary authentic, respectful, and focused on sustainable eco-cultural tourism in Jharkhand that benefits local communities.
"""
    
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"itinerary": result.strip()}
    except Exception as e:
        return {"itinerary": "", "warning": str(e)}