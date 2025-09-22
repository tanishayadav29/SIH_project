import streamlit as st
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import os
from agents import generate_itinerary, recommend_activities, fetch_useful_links, weather_forecaster, packing_list_generator, food_culture_recommender, chat_agent, safety_constraints
from utils_export import export_to_pdf

# Load environment variables
load_dotenv()

# Initialize LLM
st.set_page_config(page_title="AI Travel Planner", layout="wide")
try:
    llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434")
except Exception as e:
    st.error(f"LLM initialization failed: {str(e)}")
    st.stop()

# Initialize GoogleSerperAPIWrapper
try:
    search = GoogleSerperAPIWrapper()
except Exception as e:
    st.error(f"Serper API initialization failed: {str(e)}")
    st.stop()

# Define state
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

# ------------------- LangGraph -------------------

workflow = StateGraph(GraphState)
workflow.add_node("generate_itinerary", generate_itinerary.generate_itinerary)
workflow.add_node("recommend_activities", recommend_activities.recommend_activities)
workflow.add_node("fetch_useful_links", fetch_useful_links.fetch_useful_links)
workflow.add_node("weather_forecaster", weather_forecaster.weather_forecaster)
workflow.add_node("packing_list_generator", packing_list_generator.packing_list_generator)
workflow.add_node("food_culture_recommender", food_culture_recommender.food_culture_recommender)
workflow.add_node("safety_constraints_node", safety_constraints.safety_constraints_agent)
workflow.add_node("chat", chat_agent.chat_node)
workflow.set_entry_point("generate_itinerary")

workflow.add_edge("generate_itinerary", "recommend_activities")
workflow.add_edge("recommend_activities", "fetch_useful_links")
workflow.add_edge("fetch_useful_links", "weather_forecaster")
workflow.add_edge("weather_forecaster", "packing_list_generator")
workflow.add_edge("packing_list_generator", "food_culture_recommender")
workflow.add_edge("food_culture_recommender", "safety_constraints_node")
workflow.add_edge("safety_constraints_node", "chat")


workflow.add_edge("generate_itinerary", END)
workflow.add_edge("recommend_activities", END)
workflow.add_edge("fetch_useful_links", END)
workflow.add_edge("weather_forecaster", END)
workflow.add_edge("packing_list_generator", END)
workflow.add_edge("food_culture_recommender", END)
workflow.add_edge("safety_constraints_node", END)
workflow.add_edge("chat", END)
graph = workflow.compile()

# ------------------- UI -------------------

st.markdown("# 🌿 Jharkhand Eco-Cultural Tourism Planner")
st.markdown("### Discover the natural beauty and rich tribal heritage of Jharkhand")

if "state" not in st.session_state:
    st.session_state.state = {
        "preferences_text": "",
        "preferences": {},
        "itinerary": "",
        "activity_suggestions": "",
        "useful_links": [],
        "weather_forecast": "",
        "packing_list": "",
        "food_culture_info": "",
        "safety_constraints": "",
        "chat_history": [],
        "user_question": "",
        "chat_response": ""
    }

with st.form("travel_form"):
    col1, col2 = st.columns(2)
    with col1:
        # Jharkhand-specific destination options
        destination_options = [
            "Explore Jharkhand (General)",
            "Ranchi & Surroundings", 
            "Deoghar Pilgrimage Circuit",
            "Netarhat Hill Station",
            "Betla National Park",
            "Tribal Villages & Culture",
            "Waterfalls Circuit",
            "Custom Destination"
        ]
        destination = st.selectbox("🎯 Destination Focus", destination_options)
        
        # Custom destination input if selected
        if destination == "Custom Destination":
            custom_dest = st.text_input("Specify your destination")
            destination = custom_dest if custom_dest else "Explore Jharkhand (General)"
        
        month = st.selectbox("📅 Month of Travel", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        duration = st.slider("⏱️ Number of Days", 1, 30, 7)
        num_people = st.selectbox("👥 Number of People", ["1", "2", "3", "4-6", "7-10", "10+"])
        
        # Jharkhand-specific tourism types
        tourism_type = st.selectbox("🌿 Tourism Type", [
            "Eco-Tourism & Nature",
            "Tribal Culture & Heritage", 
            "Pilgrimage & Spiritual",
            "Adventure & Trekking",
            "Mixed Experience",
            "Photography & Wildlife"
        ])
        
        # Tribal culture interest level
        tribal_interest = st.select_slider("🏛️ Tribal Culture Interest", 
                                         options=["Low", "Medium", "High", "Very High"],
                                         value="Medium")
        
    with col2:
        # Mobility and activity level
        mobility_level = st.selectbox("🚶 Mobility Level", [
            "Easy (No trekking)",
            "Moderate (Light walking)", 
            "Active (Moderate trekking)",
            "Adventure (Challenging treks)"
        ])
        
        # Accommodation preference
        accommodation_type = st.selectbox("🏠 Accommodation Preference", [
            "Homestays (Tribal villages)",
            "Eco-lodges & Nature stays",
            "Hotels & Resorts", 
            "Mixed (Homestays + Hotels)",
            "Budget-friendly options"
        ])
        
        # Language preference
        language_preference = st.selectbox("🗣️ Language Preference", [
            "English",
            "Hindi", 
            "English + Hindi",
            "Local languages welcome"
        ])
        
        # Budget in INR
        budget_range = st.selectbox("💰 Budget Range (INR)", [
            "Budget (₹500-1500/day)",
            "Mid-Range (₹1500-3000/day)", 
            "Comfortable (₹3000-5000/day)",
            "Luxury (₹5000+/day)"
        ])
        
        # Special interests
        special_interests = st.multiselect("✨ Special Interests", [
            "Tribal festivals & ceremonies",
            "Handicraft workshops", 
            "Wildlife photography",
            "Local cuisine & cooking",
            "Traditional music & dance",
            "Nature photography",
            "Spiritual experiences",
            "Adventure activities"
        ])
        
        comments = st.text_area("💭 Additional Comments or Special Requests")
    
    submit_btn = st.form_submit_button("🌿 Generate Jharkhand Itinerary")

# Add helpful information about Jharkhand tourism
with st.expander("ℹ️ About Jharkhand Eco-Cultural Tourism", expanded=False):
    st.markdown("""
    **🌿 What makes Jharkhand special?**
    - **Rich Tribal Heritage**: Home to Santhal, Munda, and Oraon communities with vibrant cultural traditions
    - **Natural Beauty**: Stunning waterfalls, national parks, and hill stations
    - **Spiritual Significance**: Sacred temples and pilgrimage sites
    - **Sustainable Tourism**: Emphasis on community-based and eco-friendly experiences
    
    **📅 Best Times to Visit:**
    - **October-March**: Ideal for wildlife safaris, trekking, and outdoor activities
    - **July-September**: Perfect for waterfall visits (monsoon season)
    - **Festival Season**: October-November for cultural festivals like Sohrai and Karam
    
    **🏛️ Cultural Respect Guidelines:**
    - Always ask permission before photographing people
    - Dress modestly, especially in religious places
    - Learn basic greetings in local languages
    - Support local artisans by purchasing authentic handicrafts
    - Respect sacred spaces and tribal traditions
    """)

if submit_btn:
    # Create comprehensive preferences text for Jharkhand context
    preferences_text = f"""Jharkhand Eco-Cultural Tourism Preferences:
Destination Focus: {destination}
Month: {month}
Duration: {duration} days
Number of People: {num_people}
Tourism Type: {tourism_type}
Tribal Culture Interest: {tribal_interest}
Mobility Level: {mobility_level}
Accommodation: {accommodation_type}
Language Preference: {language_preference}
Budget Range: {budget_range}
Special Interests: {', '.join(special_interests) if special_interests else 'None specified'}
Additional Comments: {comments}"""
    
    preferences = {
        "destination": destination,
        "month": month,
        "duration": duration,
        "num_people": num_people,
        "tourism_type": tourism_type,
        "tribal_interest": tribal_interest,
        "mobility_level": mobility_level,
        "accommodation_type": accommodation_type,
        "language_preference": language_preference,
        "budget_range": budget_range,
        "special_interests": special_interests,
        "comments": comments,
        # Keep legacy fields for compatibility
        "holiday_type": tourism_type,
        "budget_type": budget_range
    }
    st.session_state.state.update({
        "preferences_text": preferences_text,
        "preferences": preferences,
        "chat_history": [],
        "user_question": "",
        "chat_response": "",
        "activity_suggestions": "",
        "useful_links": [],
        "weather_forecast": "",
        "packing_list": "",
        "food_culture_info": "",
        "safety_constraints": ""
    })
    with st.spinner("Generating itinerary..."):
        result = graph.invoke(st.session_state.state)
        st.session_state.state.update(result)
        if result.get("itinerary"):
            st.success("🌿 Your Jharkhand Eco-Cultural Itinerary is Ready!")
            st.info("💡 Tip: Check the seasonal information and cultural guidelines for the best experience")
        else:
            st.error("❌ Failed to generate itinerary. Please try again.")

# Layout
if st.session_state.state.get("itinerary"):
    col_itin, col_chat = st.columns([3, 2])

    with col_itin:
        st.markdown("### 🌿 Your Jharkhand Eco-Cultural Itinerary")
        st.markdown(st.session_state.state["itinerary"])
        
        # Add cultural context information
        if st.session_state.state.get("preferences", {}).get("tribal_interest") in ["High", "Very High"]:
            st.info("🏛️ **Cultural Focus**: Your itinerary emphasizes tribal culture experiences. Remember to respect local customs and traditions.")

        # All agent buttons in two rows
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🎯 Tribal Activities"):
                with st.spinner("Finding cultural activities..."):
                    result = recommend_activities.recommend_activities(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn2:
            if st.button("🔗 Local Resources"):
                with st.spinner("Fetching local resources..."):
                    result = fetch_useful_links.fetch_useful_links(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn3:
            if st.button("🌤️ Weather & Seasons"):
                with st.spinner("Checking seasonal conditions..."):
                    result = weather_forecaster.weather_forecaster(st.session_state.state)
                    st.session_state.state.update(result)
        
        col_btn4, col_btn5, col_btn6 = st.columns(3)
        with col_btn4:
            if st.button("🎒 Packing Guide"):
                with st.spinner("Creating packing list..."):
                    result = packing_list_generator.packing_list_generator(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn5:
            if st.button("🍽️ Local Cuisine"):
                with st.spinner("Exploring local food & culture..."):
                    result = food_culture_recommender.food_culture_recommender(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn6:
            if st.button("🛡️ Safety & Permits"):
                with st.spinner("Checking safety requirements..."):
                    result = safety_constraints.safety_constraints_agent(st.session_state.state)
                    st.session_state.state.update(result)

        # Display all agent outputs in expanders
        if st.session_state.state.get("activity_suggestions"):
            with st.expander("🎯 Tribal & Cultural Activities", expanded=False):
                st.markdown(st.session_state.state["activity_suggestions"])

        if st.session_state.state.get("useful_links"):
            with st.expander("🔗 Local Resources & Contacts", expanded=False):
                for link in st.session_state.state["useful_links"]:
                    st.markdown(f"- [{link['title']}]({link['link']})")

        if st.session_state.state.get("weather_forecast"):
            with st.expander("🌤️ Weather & Seasonal Conditions", expanded=False):
                st.markdown(st.session_state.state["weather_forecast"])

        if st.session_state.state.get("packing_list"):
            with st.expander("🎒 Jharkhand Packing Guide", expanded=False):
                st.markdown(st.session_state.state["packing_list"])

        if st.session_state.state.get("food_culture_info"):
            with st.expander("🍽️ Local Cuisine & Cultural Etiquette", expanded=False):
                st.markdown(st.session_state.state["food_culture_info"])

        if st.session_state.state.get("safety_constraints"):
            with st.expander("🛡️ Safety Guidelines & Permit Requirements", expanded=False):
                st.markdown(st.session_state.state["safety_constraints"])

        # Export PDF button
        if st.button("Export as PDF"):
            pdf_path = export_to_pdf(st.session_state.state["itinerary"])
            if pdf_path:
                with open(pdf_path, "rb") as f:
                    st.download_button("Download Itinerary PDF", f, file_name="itinerary.pdf")

    with col_chat:
        st.markdown("### 💬 Ask About Your Jharkhand Experience")
        st.markdown("*Get personalized advice about tribal culture, local customs, and travel tips*")
        
        for chat in st.session_state.state["chat_history"]:
            with st.chat_message("user"):
                st.markdown(chat["question"])
            with st.chat_message("assistant"):
                st.markdown(chat["response"])

        if user_input := st.chat_input("Ask about tribal culture, local customs, or travel tips..."):
            st.session_state.state["user_question"] = user_input
            with st.spinner("Getting local insights..."):
                result = chat_agent.chat_node(st.session_state.state)
                st.session_state.state.update(result)
                st.rerun()
else:
    st.info("🌿 Fill the form above to generate your personalized Jharkhand eco-cultural itinerary!")