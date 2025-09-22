# Jharkhand Tourism Data

This directory contains comprehensive data for Jharkhand eco-cultural tourism itinerary planning.

## Files Overview

### 1. `jharkhand_pois.json`
**Main Points of Interest Database**

Contains detailed information about 10 key tourist destinations in Jharkhand:

- **Natural Sites**: Netarhat, Betla National Park, Hundru Falls, Jonha Falls, Dassam Falls, Patratu Dam, Hazaribagh National Park
- **Religious Sites**: Baidyanath Temple (Deoghar), Basukinath Temple
- **Cultural Sites**: Tribal Research Institute & Museum

**Data Structure for each POI:**
- Basic info (name, location, coordinates)
- Seasonal information (best/avoid seasons)
- Practical details (entry fees, opening hours, duration)
- Activities and nearby attractions
- Safety notes and accessibility information
- Cultural significance and local context

### 2. `tribal_culture_data.json`
**Tribal Culture and Community Information**

Comprehensive data about Jharkhand's tribal communities:

- **Tribal Communities**: Santhal, Munda, Oraon with their cultural practices
- **Cultural Festivals**: Sohrai, Karam, Sarhul festivals with timing and activities
- **Handicraft Workshops**: Terracotta, bamboo craft, textile workshops
- **Homestay Options**: Authentic village experiences with tribal families
- **Local Guides**: Specialized guides for cultural and nature tours
- **Cultural Etiquette**: Guidelines for respectful interaction with tribal communities

### 3. `seasonal_constraints.json`
**Seasonal Travel Information**

Detailed seasonal analysis for Jharkhand tourism:

- **Seasonal Weather**: Monsoon, Winter, Summer, Post-Monsoon conditions
- **Monthly Recommendations**: Best activities and considerations for each month
- **Accessibility Matrix**: Which attractions are accessible in which seasons
- **Safety Precautions**: Season-specific safety guidelines
- **Activity Recommendations**: What to do and avoid in each season

### 4. `data_loader.py`
**Utility Module for Data Access**

Python utility class `JharkhandDataLoader` with methods to:

- Load and cache data files
- Filter POIs by category, season, or search query
- Get tribal festivals and workshops by month/location
- Retrieve seasonal recommendations and accessibility info
- Search cultural etiquette and guide information

## Usage Examples

```python
from data.data_loader import jharkhand_data

# Get all nature POIs
nature_pois = jharkhand_data.get_pois_by_category("nature")

# Get POIs suitable for November
november_pois = jharkhand_data.get_pois_by_season("november")

# Get tribal festivals in August
august_festivals = jharkhand_data.get_tribal_festivals_by_month("august")

# Get handicraft workshops in Ranchi
ranchi_workshops = jharkhand_data.get_handicraft_workshops("ranchi")

# Get seasonal recommendations for March
march_recommendations = jharkhand_data.get_seasonal_recommendations("march")

# Check accessibility of national parks in July
accessibility = jharkhand_data.get_accessibility_info("national_parks", "july")
```

## Data Features

### Cultural Sensitivity
- All data includes Hindi translations
- Cultural etiquette guidelines for respectful tourism
- Emphasis on community-based and sustainable tourism

### Practical Information
- Real coordinates and travel distances
- Entry fees in INR
- Seasonal accessibility information
- Safety considerations and permit requirements

### Sustainability Focus
- Emphasis on eco-tourism and cultural preservation
- Community-based accommodation options
- Local guide recommendations
- Support for tribal artisans and crafts

## Data Sources

- Jharkhand Tourism Department
- Local community research
- Tribal cultural documentation
- Seasonal weather patterns
- Accessibility and safety guidelines

## Updates

This data is designed to be easily expandable. New POIs, festivals, workshops, and seasonal information can be added following the existing data structure patterns.

Last Updated: January 2024