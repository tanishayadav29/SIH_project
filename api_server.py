import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import existing agents and graph
from agents import (
    generate_itinerary,
    safety_constraints,
    cultural_recommender,
    food_culture_recommender,
    recommend_activities,
    packing_list_generator,
    weather_forecaster,
)
from agents import chat_agent
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

load_dotenv()

class GraphState(TypedDict):
    preferences_text: str
    preferences: dict
    itinerary: str
    activity_suggestions: str
    useful_links: list[dict]
    weather_forecast: str
    packing_list: str
    food_culture_info: str
    safety_constraints: str
    chat_history: Annotated[list[dict], "List of question-response pairs"]
    user_question: str
    chat_response: str

# Build a minimal graph reusing your existing functions
workflow = StateGraph(GraphState)
workflow.add_node("generate_itinerary", generate_itinerary.generate_itinerary)
workflow.set_entry_point("generate_itinerary")
workflow.add_edge("generate_itinerary", END)
graph = workflow.compile()

app = FastAPI(title="Travel Itinerary Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Preferences(BaseModel):
    destination: str
    month: str
    duration: int
    num_people: str
    tourism_type: str
    tribal_interest: str
    mobility_level: str
    accommodation_type: str
    language_preference: str
    budget_range: str
    special_interests: list[str] = []
    comments: str | None = ""

class GenerateRequest(BaseModel):
    preferences: Preferences

@app.post("/api/generate_itinerary")
def api_generate_itinerary(payload: GenerateRequest):
    try:
        prefs = payload.preferences.dict()
        preferences_text = (
            f"Destination Focus: {prefs['destination']}\n"
            f"Month: {prefs['month']}\n"
            f"Duration: {prefs['duration']} days\n"
            f"Number of People: {prefs['num_people']}\n"
            f"Tourism Type: {prefs['tourism_type']}\n"
            f"Tribal Culture Interest: {prefs['tribal_interest']}\n"
            f"Mobility Level: {prefs['mobility_level']}\n"
            f"Accommodation: {prefs['accommodation_type']}\n"
            f"Language Preference: {prefs['language_preference']}\n"
            f"Budget Range: {prefs['budget_range']}\n"
            f"Special Interests: {', '.join(prefs.get('special_interests', [])) or 'None specified'}\n"
            f"Additional Comments: {prefs.get('comments') or ''}"
        )

        state = {
            "preferences_text": preferences_text,
            "preferences": prefs,
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "safety_constraints": "",
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
        }

        result = graph.invoke(state)
        return {
            "itinerary": result.get("itinerary", ""),
            "activity_suggestions": result.get("activity_suggestions", ""),
            "useful_links": result.get("useful_links", []),
            "weather_forecast": result.get("weather_forecast", ""),
            "packing_list": result.get("packing_list", ""),
            "food_culture_info": result.get("food_culture_info", ""),
            "safety_constraints": result.get("safety_constraints", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SafetyPromptRequest(BaseModel):
    prompt: str


@app.post("/api/safety_guidance")
def api_safety_guidance(payload: SafetyPromptRequest):
    try:
        # Map the free-form prompt to the agent's expected state shape.
        # Using the prompt as destination enables keyword-based rules (e.g., Betla) to trigger.
        state = {
            "preferences_text": f"Safety guidance request for: {payload.prompt}",
            "preferences": {
                "destination": payload.prompt,
                "month": "October",
                "tourism_type": "Mixed Experience",
                "mobility_level": "Moderate (Light walking)",
                "special_interests": [],
            },
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "safety_constraints": "",
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
        }

        result = safety_constraints.safety_constraints_agent(state)
        return {"guidance": result.get("safety_constraints", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SimplePromptRequest(BaseModel):
    prompt: str


@app.post("/api/culture_recommendations")
def api_culture_recommendations(payload: SimplePromptRequest):
    try:
        state = {
            "preferences_text": f"Culture recommendations for: {payload.prompt}",
            "preferences": {
                "destination": payload.prompt,
                "month": "October",
                "tribal_interest": "Medium",
                "mobility_level": "Moderate (Light walking)",
                "budget_range": "Mid-Range (₹1500-3000/day)",
                "special_interests": [],
            },
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "safety_constraints": "",
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
        }
        result = cultural_recommender.cultural_recommender(state)
        return {"recommendations": result.get("cultural_recommendations", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/food_recommendations")
def api_food_recommendations(payload: SimplePromptRequest):
    try:
        state = {
            "preferences_text": f"Food recommendations for: {payload.prompt}",
            "preferences": {
                "destination": payload.prompt,
                "month": "October",
                "budget_range": "Mid-Range (₹1500-3000/day)",
                "tribal_interest": "Medium",
                "special_interests": ["Local cuisine & cooking"],
            },
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "safety_constraints": "",
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
        }
        result = food_culture_recommender.food_culture_recommender(state)
        return {"recommendations": result.get("food_culture_info", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/activities_recommendations")
def api_activities_recommendations(payload: SimplePromptRequest):
    try:
        # Use the prompt as the destination context to trigger place-specific data
        state = {
            "preferences_text": f"Activities recommendations for: {payload.prompt}",
            "preferences": {
                "destination": payload.prompt,
                "month": "October",
                "tourism_type": "Mixed Experience",
                "tribal_interest": "Medium",
                "mobility_level": "Moderate (Light walking)",
                "budget_range": "Mid-Range (₹1500-3000/day)",
                "special_interests": [],
            },
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "safety_constraints": "",
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
        }
        result = recommend_activities.recommend_activities(state)
        return {"recommendations": result.get("activity_suggestions", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PackListRequest(BaseModel):
    destination: str
    season: str
    activities: str
    days: int


@app.post("/api/pack_list")
def api_pack_list(payload: PackListRequest):
    try:
        # Map request to the packing list agent's expected state
        state = {
            "preferences_text": (
                f"Pack list for {payload.destination}, {payload.season}, {payload.days} days, activities: {payload.activities}"
            ),
            "preferences": {
                "destination": payload.destination,
                "month": payload.season,
                "duration": payload.days,
                "holiday_type": payload.activities,
            },
            "packing_list": "",
        }
        result = packing_list_generator.packing_list_generator(state)
        return {"list": result.get("packing_list", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WeatherRequest(BaseModel):
    location: str
    date: str | None = None


@app.post("/api/weather_forecast")
def api_weather_forecast(payload: WeatherRequest):
    try:
        # Derive month name from date if provided, else default to October
        month = "October"
        try:
            if payload.date:
                # Expecting YYYY-MM-DD
                parts = payload.date.split("-")
                if len(parts) == 3:
                    import calendar
                    month_num = int(parts[1])
                    month = calendar.month_name[month_num]
        except Exception:
            pass

        state = {
            "preferences_text": f"Weather forecast for {payload.location} on {payload.date or month}",
            "preferences": {
                "destination": payload.location,
                "month": month,
                "tourism_type": "Mixed Experience",
                "mobility_level": "Moderate (Light walking)",
            },
            "weather_forecast": "",
        }
        result = weather_forecaster.weather_forecaster(state)
        return {"forecast": result.get("weather_forecast", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ChatRequest(BaseModel):
    prompt: str


@app.post("/api/chat")
def api_chat(payload: ChatRequest):
    try:
        state = {
            "preferences_text": f"Chat prompt: {payload.prompt}",
            "preferences": {},
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "safety_constraints": "",
            "chat_history": [],
            "user_question": payload.prompt,
            "chat_response": "",
        }
        result = chat_agent.chat_node(state)
        return {"response": result.get("chat_response", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)


