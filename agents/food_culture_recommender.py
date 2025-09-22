from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama
import json
import sys
import os

# Add data directory to path to import our data loader
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from data_loader import jharkhand_data

def load_jharkhand_cuisine():
    """Load Jharkhand cuisine data"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jharkhand_cuisine.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

def get_dishes_by_preference(cuisine_data, preferences):
    """Filter dishes based on user preferences"""
    dishes = cuisine_data.get('traditional_dishes', [])
    filtered_dishes = []
    
    # Filter by dietary preferences
    dietary_prefs = preferences.get('special_interests', [])
    
    for dish in dishes:
        # Include all dishes by default, but prioritize based on interests
        if "Local cuisine & cooking" in dietary_prefs:
            filtered_dishes.append(dish)
        elif dish['category'] in ['main_course', 'bread', 'side_dish']:
            filtered_dishes.append(dish)
    
    return filtered_dishes[:6]  # Limit to 6 dishes for better focus

def get_dining_recommendations_by_location(destination, cuisine_data):
    """Get dining recommendations based on destination"""
    regional_specialties = cuisine_data.get('regional_specialties', {})
    
    if "Ranchi" in destination:
        return regional_specialties.get('ranchi', [])
    elif "Deoghar" in destination:
        return regional_specialties.get('deoghar', [])
    elif "Dumka" in destination:
        return regional_specialties.get('dumka', [])
    elif "Netarhat" in destination:
        return regional_specialties.get('netarhat', [])
    else:
        return ["Traditional Jharkhand cuisine", "Local tribal food", "Regional specialties"]

def food_culture_recommender(state):
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
    
    # Extract preferences
    preferences = state.get('preferences', {})
    destination = preferences.get('destination', 'Jharkhand')
    budget_range = preferences.get('budget_range', 'Mid-Range (₹1500-3000/day)')
    tribal_interest = preferences.get('tribal_interest', 'Medium')
    special_interests = preferences.get('special_interests', [])
    month = preferences.get('month', 'October').lower()
    
    # Load Jharkhand cuisine data
    cuisine_data = load_jharkhand_cuisine()
    
    # Get filtered dishes
    recommended_dishes = get_dishes_by_preference(cuisine_data, preferences)
    
    # Get location-specific recommendations
    location_recommendations = get_dining_recommendations_by_location(destination, cuisine_data)
    
    # Get cultural etiquette
    try:
        cultural_etiquette = jharkhand_data.get_cultural_etiquette()
    except Exception as e:
        cultural_etiquette = {}
    
    # Get cooking experiences
    cooking_experiences = cuisine_data.get('cooking_experiences', [])
    
    # Get food markets
    food_markets = cuisine_data.get('food_markets', [])
    
    # Get dining etiquette
    dining_etiquette = cuisine_data.get('dining_etiquette', {})
    
    prompt = f"""
You are a Jharkhand cuisine and culture specialist. Provide comprehensive food and cultural guidance for travelers visiting Jharkhand.

**TRAVEL CONTEXT:**
- Destination: {destination}
- Month: {month.title()}
- Budget Range: {budget_range}
- Tribal Interest Level: {tribal_interest}
- Special Interests: {special_interests}

**JHARKHAND CUISINE OVERVIEW:**
{json.dumps(cuisine_data.get('cuisine_overview', {}), indent=2)}

**RECOMMENDED TRADITIONAL DISHES:**
{json.dumps(recommended_dishes, indent=2)}

**LOCATION-SPECIFIC DINING:**
{json.dumps(location_recommendations, indent=2)}

**COOKING EXPERIENCES:**
{json.dumps(cooking_experiences, indent=2)}

**FOOD MARKETS TO VISIT:**
{json.dumps(food_markets, indent=2)}

**DINING ETIQUETTE:**
{json.dumps(dining_etiquette, indent=2)}

**CULTURAL ETIQUETTE:**
{json.dumps(cultural_etiquette, indent=2)}

**INSTRUCTIONS:**
1. Focus on authentic Jharkhand tribal cuisine and traditional dishes
2. Include seasonal considerations for {month}
3. Provide budget-appropriate dining suggestions
4. Include cultural context and significance of dishes
5. Suggest cooking experiences and food markets
6. Provide detailed dining etiquette and cultural guidelines
7. Include practical information: locations, costs, timing
8. Emphasize respect for tribal food traditions
9. Suggest ways to support local food producers and artisans
10. Include dietary considerations and allergy information

**FORMAT:**
- Organize into clear sections: Traditional Dishes, Dining Options, Cultural Etiquette
- Include dish names in English, Hindi, and local languages
- Provide cultural significance and origin of each dish
- Add practical details: where to find, cost, best time to eat
- Include cultural etiquette reminders
- Suggest cooking workshops and food experiences
- Provide food market recommendations

**CULTURAL SENSITIVITY:**
- Emphasize respect for tribal food traditions
- Include guidance on appropriate dining behavior
- Suggest ways to support local food producers
- Provide context about cultural significance of food
- Include information about traditional cooking methods
- Emphasize the importance of food in tribal culture

Make recommendations that promote authentic culinary experiences while respecting Jharkhand's tribal food traditions and supporting local communities.
"""
    
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"food_culture_info": result.strip()}
    except Exception as e:
        return {"food_culture_info": "", "warning": str(e)}