import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import existing agents and graph
from agents import generate_itinerary
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

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)


