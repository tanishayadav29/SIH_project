from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama
import json
import sys
import os
import requests
from datetime import datetime, timedelta

# Add data directory to path to import our data loader
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from data_loader import jharkhand_data

def get_jharkhand_weather_data(city="Ranchi"):
    """Get weather data from Indian weather API (OpenWeatherMap)"""
    try:
        # Using OpenWeatherMap API (free tier available)
        # You can replace with other Indian weather APIs like IMD
        api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        
        if api_key == 'demo_key':
            # Return demo data if no API key is provided
            return get_demo_weather_data(city)
        
        # Jharkhand city coordinates
        city_coords = {
            "ranchi": {"lat": 23.3441, "lon": 85.3096},
            "deoghar": {"lat": 24.4833, "lon": 86.7000},
            "dumka": {"lat": 24.2667, "lon": 87.2500},
            "netarhat": {"lat": 23.4833, "lon": 84.7167},
            "hazaribagh": {"lat": 24.0000, "lon": 85.3667}
        }
        
        city_lower = city.lower()
        if city_lower in city_coords:
            coords = city_coords[city_lower]
        else:
            coords = city_coords["ranchi"]  # Default to Ranchi
        
        # Get current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={api_key}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        
        # Get 5-day forecast
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            
            return {
                "current": {
                    "temperature": current_data['main']['temp'],
                    "feels_like": current_data['main']['feels_like'],
                    "humidity": current_data['main']['humidity'],
                    "description": current_data['weather'][0]['description'],
                    "wind_speed": current_data['wind']['speed'],
                    "visibility": current_data.get('visibility', 0) / 1000  # Convert to km
                },
                "forecast": forecast_data['list'][:8],  # Next 24 hours
                "city": current_data['name']
            }
        else:
            return get_demo_weather_data(city)
            
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_demo_weather_data(city)

def get_demo_weather_data(city="Ranchi"):
    """Demo weather data for demonstration purposes"""
    month = datetime.now().month
    
    # Seasonal weather patterns for Jharkhand
    if month in [6, 7, 8, 9]:  # Monsoon
        return {
            "current": {
                "temperature": 28,
                "feels_like": 32,
                "humidity": 85,
                "description": "heavy rain",
                "wind_speed": 15,
                "visibility": 2
            },
            "forecast": [],
            "city": city,
            "demo": True
        }
    elif month in [12, 1, 2]:  # Winter
        return {
            "current": {
                "temperature": 18,
                "feels_like": 16,
                "humidity": 45,
                "description": "clear sky",
                "wind_speed": 8,
                "visibility": 10
            },
            "forecast": [],
            "city": city,
            "demo": True
        }
    else:  # Summer/Post-monsoon
        return {
            "current": {
                "temperature": 32,
                "feels_like": 36,
                "humidity": 60,
                "description": "partly cloudy",
                "wind_speed": 12,
                "visibility": 8
            },
            "forecast": [],
            "city": city,
            "demo": True
        }

def get_seasonal_weather_analysis(month, weather_data):
    """Analyze weather based on Jharkhand's seasonal patterns"""
    month_num = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }.get(month.lower(), 10)
    
    if month_num in [6, 7, 8, 9]:
        season = "monsoon"
        analysis = {
            "season": "Monsoon Season",
            "characteristics": ["Heavy rainfall", "High humidity", "Reduced visibility", "Possible flooding"],
            "travel_impact": ["Road conditions poor", "Some areas inaccessible", "National parks closed", "Waterfalls spectacular"],
            "recommendations": ["Carry rain gear", "Check road conditions", "Avoid remote areas", "Indoor activities preferred"]
        }
    elif month_num in [12, 1, 2]:
        season = "winter"
        analysis = {
            "season": "Winter Season",
            "characteristics": ["Cool temperatures", "Clear skies", "Low humidity", "Good visibility"],
            "travel_impact": ["Excellent for outdoor activities", "Best for wildlife safaris", "Ideal for trekking", "Peak tourist season"],
            "recommendations": ["Carry warm clothing", "Perfect for photography", "All attractions accessible", "Book accommodations early"]
        }
    elif month_num in [3, 4, 5]:
        season = "summer"
        analysis = {
            "season": "Summer Season",
            "characteristics": ["Hot temperatures", "Dry weather", "Moderate humidity", "Good visibility"],
            "travel_impact": ["Very hot during peak hours", "Good for early morning activities", "Hill stations provide relief", "Waterfalls have less water"],
            "recommendations": ["Stay hydrated", "Plan early morning activities", "Visit hill stations", "Avoid midday outdoor activities"]
        }
    else:  # October, November
        season = "post_monsoon"
        analysis = {
            "season": "Post-Monsoon Season",
            "characteristics": ["Pleasant temperatures", "Lush greenery", "Occasional light showers", "Good visibility"],
            "travel_impact": ["Ideal for all activities", "Beautiful landscapes", "Good road conditions", "Festival season begins"],
            "recommendations": ["Perfect for outdoor activities", "Carry light rain gear", "Excellent for photography", "Cultural festivals available"]
        }
    
    return analysis

def weather_forecaster(state):
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
    
    # Extract preferences
    preferences = state.get('preferences', {})
    destination = preferences.get('destination', 'Jharkhand')
    month = preferences.get('month', 'October').lower()
    tourism_type = preferences.get('tourism_type', 'Mixed Experience')
    mobility_level = preferences.get('mobility_level', 'Moderate (Light walking)')
    
    # Get weather data
    weather_data = get_jharkhand_weather_data(destination)
    
    # Get seasonal analysis
    seasonal_analysis = get_seasonal_weather_analysis(month, weather_data)
    
    # Get seasonal constraints
    try:
        seasonal_constraints = jharkhand_data.get_seasonal_recommendations(month)
    except Exception as e:
        seasonal_constraints = {}
    
    # Get accessibility information
    try:
        accessibility_info = {
            "national_parks": jharkhand_data.get_accessibility_info("national_parks", month),
            "waterfalls": jharkhand_data.get_accessibility_info("waterfalls", month),
            "hill_stations": jharkhand_data.get_accessibility_info("hill_stations", month),
            "temples": jharkhand_data.get_accessibility_info("temples", month)
        }
    except Exception as e:
        accessibility_info = {}
    
    prompt = f"""
You are a Jharkhand weather specialist and seasonal tourism expert. Provide comprehensive weather analysis and travel advice for Jharkhand.

**TRAVEL CONTEXT:**
- Destination: {destination}
- Month: {month.title()}
- Tourism Type: {tourism_type}
- Mobility Level: {mobility_level}

**CURRENT WEATHER DATA:**
{json.dumps(weather_data, indent=2)}

**SEASONAL ANALYSIS:**
{json.dumps(seasonal_analysis, indent=2)}

**SEASONAL CONSTRAINTS:**
{json.dumps(seasonal_constraints, indent=2)}

**ACCESSIBILITY INFORMATION:**
{json.dumps(accessibility_info, indent=2)}

**INSTRUCTIONS:**
1. Provide detailed weather forecast for {month} in Jharkhand
2. Include seasonal characteristics and travel impact
3. Give specific advice based on tourism_type and mobility_level
4. Include accessibility information for different attractions
5. Provide practical recommendations for clothing and gear
6. Include safety considerations for the season
7. Suggest optimal timing for different activities
8. Include monsoon-specific warnings if applicable
9. Provide alternative indoor activities if weather is challenging
10. Include cultural and festival considerations for the season

**FORMAT:**
- Current Weather Conditions
- Seasonal Overview and Characteristics
- Travel Impact and Accessibility
- Practical Recommendations (clothing, gear, timing)
- Safety Considerations
- Activity-Specific Weather Advice
- Alternative Indoor Activities (if needed)
- Cultural and Festival Timing

**SEASONAL FOCUS:**
- Monsoon (June-September): Heavy rain, accessibility issues, indoor activities
- Winter (December-February): Cool, clear, ideal for outdoor activities
- Summer (March-May): Hot, dry, early morning activities recommended
- Post-Monsoon (October-November): Pleasant, lush, perfect for all activities

**SAFETY EMPHASIS:**
- Monsoon safety: Road conditions, flooding, visibility
- Heat safety: Hydration, sun protection, timing
- Cold weather: Warm clothing, fog conditions
- General: Weather-related health considerations

Make the weather forecast practical, safety-focused, and tailored to Jharkhand's specific seasonal patterns and tourism needs.
"""
    
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"weather_forecast": result.strip()}
    except Exception as e:
        return {"weather_forecast": "", "warning": str(e)}