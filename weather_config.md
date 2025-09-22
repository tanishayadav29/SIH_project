# Weather API Configuration

## OpenWeatherMap API Setup

The weather agent now supports real-time weather data from OpenWeatherMap API. Here's how to set it up:

### 1. Get API Key
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard

### 2. Set Environment Variable
Add your API key to your environment:

**Windows:**
```cmd
set OPENWEATHER_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export OPENWEATHER_API_KEY=your_api_key_here
```

**Or create a .env file:**
```
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. Demo Mode
If no API key is provided, the system will use demo weather data based on Jharkhand's seasonal patterns.

## Supported Cities

The weather agent supports these Jharkhand cities:
- Ranchi (default)
- Deoghar
- Dumka
- Netarhat
- Hazaribagh

## Features

### Real-time Weather Data
- Current temperature, humidity, wind speed
- Weather description and visibility
- 5-day forecast (when API key is available)

### Seasonal Analysis
- **Monsoon (June-September)**: Heavy rain, accessibility issues
- **Winter (December-February)**: Cool, clear, ideal for outdoor activities
- **Summer (March-May)**: Hot, dry, early morning activities recommended
- **Post-Monsoon (October-November)**: Pleasant, lush, perfect for all activities

### Accessibility Information
- National parks accessibility by season
- Waterfall conditions and best visiting times
- Hill station weather considerations
- Temple visit weather advice

### Safety Considerations
- Monsoon safety warnings
- Heat safety recommendations
- Cold weather precautions
- Weather-related health advice

## Alternative APIs

You can replace OpenWeatherMap with other Indian weather APIs:
- IMD (India Meteorological Department)
- AccuWeather
- Weather.com
- Local Indian weather services

Just modify the `get_jharkhand_weather_data()` function in `agents/weather_forecaster.py`.