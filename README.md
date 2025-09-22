# MultiAgents-with-Langgraph-TravelItineraryPlanner

Welcome to the **AI Travel Itinerary Planner**, a modular multi-agent system built with Streamlit, LangGraph, and Ollama. This application leverages multiple AI agents to generate personalized travel itineraries and provide additional travel-related insights based on user preferences. The system is designed for modularity, with agents split into individual scripts for maintainability and scalability.

- **Repository**: https://github.com/Vanya-igdtu/Jharkhand_Travel_App.git


## Overview

The AI Travel Itinerary Planner uses a LangGraph workflow to manage a set of agents that collaboratively process user inputs (e.g., destination, month, duration) to produce a detailed itinerary, activity suggestions, weather forecasts, packing lists, food/culture recommendations, useful links, and a chat interface. The system integrates with Ollama (for the `llama3.2` model) and the Google Serper API for web searches.

## Features
- Generate a detailed travel itinerary with daily plans, dining options, and downtime.
- Suggest unique local activities based on the itinerary and preferences.
- Fetch the top 5 travel guide links for the destination and month.
- Provide weather forecasts, packing lists, and food/culture recommendations.
- Offer a conversational chat to answer itinerary-related questions.
- Export the itinerary as a PDF.

## Directory Structure

```
MultiAgents-with-CrewAI-TravelItineraryPlanner/
│
├── agents/
│   ├── generate_itinerary.py
│   ├── recommend_activities.py
│   ├── fetch_useful_links.py
│   ├── weather_forecaster.py
│   ├── packing_list_generator.py
│   ├── food_culture_recommender.py
│   └── chat_agent.py
│
├── export_utils.py
├── travel_agent.py
├── requirements.txt
└── .env
```

- **agents/**: Contains individual Python scripts for each agent, modularizing the logic.
- **export_utils.py**: Houses shared utility functions (e.g., PDF export).
- **travel_agent.py**: The main Streamlit application file that orchestrates the workflow and UI.
- **requirements.txt**: Lists project dependencies.
- **.env**: Stores environment variables (e.g., `SERPER_API_KEY`).

## Setup Instructions

### Prerequisites
- Python 3.8 or higher.
- Ollama installed and running locally with the `llama3.2` model (`ollama pull llama3.2`).
- A Google Serper API key.

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/Vanya-igdtu/Jharkhand_Travel_App.git
   cd MultiAgents-with-Langgraph-TravelItineraryPlanner
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your `SERPER_API_KEY`:
     ```
     SERPER_API_KEY=your_api_key_here
     ```
4. Start Ollama locally (if not already running):
   ```bash
   ollama serve
   ```

### Running the Application
There are two ways to run the app now:

#### A) Streamlit (original)
1. Launch the Streamlit app:
   ```bash
   streamlit run travel_agent.py
   ```
2. Open your browser and navigate to the provided URL (e.g., `http://localhost:8501`).

#### B) HTML Frontend + FastAPI Backend (new)
1. Ensure Ollama is running and `llama3.2` is pulled:
   ```bash
   ollama list
   ```
   If missing, run:
   ```bash
   ollama pull llama3.2
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the API server:
   ```bash
   python -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Open the HTML frontend:
   - Option 1 (recommended): serve the static files via a simple server
     ```bash
     python -m http.server -d front-end 5500
     ```
     Then open `http://127.0.0.1:5500` and use the Itinerary tab.
   - Option 2: open `front-end/index.html` directly (if you hit CORS issues, use Option 1).

## Usage
- Enter your travel preferences (destination, month, duration, etc.) in the form.
- Click "Generate Itinerary" to create a base plan.
- Use the buttons to fetch additional details (e.g., activity suggestions, weather forecast).
- Interact with the chat to ask questions about your itinerary.
- Export the itinerary as a PDF using the "Export as PDF" button.

## Contributing
Feel free to fork this repository, submit issues, or create pull requests to enhance the project. Contributions to improve agent logic, UI, or add new features are welcome!

## License
This project is open-source. See the [LICENSE](LICENSE) file for details (if applicable).

## Acknowledgements
- Built with Streamlit, LangGraph, LangChain, and Ollama.
- Thanks to the open-source community for tools and libraries!

## Contact

