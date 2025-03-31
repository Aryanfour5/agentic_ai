import os
import json
import google.generativeai as genai
import requests
import logging
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import schedule
import threading
import time


load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Keys (Replace with your actual API keys)
GOOGLE_API_KEY = "AIzaSyBIpn7wZdStKbfe2KXKTDF3bdoCIAqZtaY"
WEATHER_API_KEY = "166db055dd5462eeee0a93c1b70b7f43"


print("GOOGLE_API_KEY:", GOOGLE_API_KEY)  # Should print the actual key
print("WEATHER_API_KEY:", WEATHER_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Store user preferences for farming
user_preferences = {}


def is_weather_related(query):
    """Check if the query is related to weather."""
    response = model.generate_content(
        f"""Determine if the following query is about weather. 
        Respond with 'yes' or 'no'. Query: '{query}'"""
    )
    return "yes" in response.text.lower()


def extract_locations(response_text):
    """Extract city names from the Gemini response."""
    try:
        cleaned_response = response_text.strip().strip("```json").strip("```").strip()
        parsed_json = json.loads(cleaned_response)
        return parsed_json.get("cities", []) if isinstance(parsed_json, dict) else []
    except json.JSONDecodeError:
        return []


def get_lat_lon(city):
    """Fetch latitude and longitude of a city using Gemini."""
    try:
        response = model.generate_content(
            f"Provide the latitude and longitude of {city} in JSON format as {{'lat': VALUE, 'lon': VALUE}}."
        )
        coordinates = json.loads(response.text.strip().strip("```json").strip("```"))
        return coordinates.get("lat"), coordinates.get("lon")
    except:
        return None, None


def get_weather_details(city):
    """Fetch weather data from OpenWeatherMap."""
    lat, lon = get_lat_lon(city)
    if lat is None or lon is None:
        return "Weather data unavailable"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
        }
    except:
        return "Weather data unavailable"


def evaluate_weather_for_farming(city, weather_data, crop=None):
    """Evaluate the weather conditions for farming based on temperature, humidity, and wind."""
    temp = weather_data["temp"]
    humidity = weather_data["humidity"]
    wind_speed = weather_data["wind_speed"]
    description = weather_data["description"]

    response = f"📍 {city}: 🌡 {temp}°C | 💧 {humidity}% | 🌬 {wind_speed} km/h | {description.capitalize()}"

    # Crop-specific logic for tomatoes, corn, etc.
    if crop == "tomato":
        if temp < 18 or temp > 30:
            response += "\n❌ Temperature is not ideal for tomatoes."
    if crop == "corn":
        if temp < 18 or temp > 35:
            response += "\n❌ Temperature is too extreme for corn."

    # Add farming decision logic
    if temp < 15 or temp > 30:
        response += "\n❌ Temperature is too extreme for most crops."
    if humidity < 40 or humidity > 70:
        response += "\n⚠️ Humidity levels are not ideal for farming."
    if wind_speed > 10:
        response += "\n⚠️ High wind speeds detected. Not ideal for outdoor farming."

    return response


def agentic_ai(user_query):
    """Process the user query and return a response."""
    if not is_weather_related(user_query):
        return "❌ You don't need to know that. Ask about the weather."

    # Check for crop preferences
    crop = None
    if "tomato" in user_query.lower():
        crop = "tomato"
    elif "corn" in user_query.lower():
        crop = "corn"

    # Store user's crop preference
    if crop:
        user_preferences[user_query] = crop

    response = model.generate_content(
        f"Extract city names from this query and return them in JSON format as {{'cities': ['city1', 'city2', ...]}}. Query: '{user_query}'"
    )
    locations = extract_locations(response.text)
    if not locations:
        return "⚠ No valid locations found. Please ask about a specific city."

    with ThreadPoolExecutor(max_workers=len(locations)) as executor:
        weather_data = {
            city: executor.submit(get_weather_details, city).result()
            for city in locations
        }

    # Evaluate and provide weather for farming decision
    farm_recommendations = []
    for city, data in weather_data.items():
        farm_recommendations.append(evaluate_weather_for_farming(city, data, crop))

    return "\n".join(farm_recommendations)


# Proactive weather notifications - Runs every day at 8 AM
def send_proactive_weather_alerts():
    # Get weather for a list of cities and send alerts (mocked for simplicity)
    cities = ["New York", "Chicago", "Los Angeles"]  # Example cities
    with ThreadPoolExecutor(max_workers=len(cities)) as executor:
        weather_updates = {
            city: executor.submit(get_weather_details, city).result() for city in cities
        }

    # Example of sending proactive weather alerts
    for city, weather in weather_updates.items():
        crop = user_preferences.get(city, "")
        alert = evaluate_weather_for_farming(city, weather, crop)
        print(f"Proactive Weather Alert for {city}: {alert}")
        # Here you would send notifications to the users about the weather


# Schedule task to check weather every day at 8 AM
schedule.every().day.at("23:48").do(send_proactive_weather_alerts)


# Function to run scheduled tasks in a background thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Start background thread for scheduled tasks
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Streamlit UI
st.set_page_config(page_title="Weather Chatbot", page_icon="⛅", layout="centered")
st.markdown(
    """<h1 style='text-align: center;'>⛅ Weather Chatbot</h1>""",
    unsafe_allow_html=True,
)

user_query = st.text_input("Ask about the weather:", "")
if st.button("Get Weather"):
    if user_query.strip():
        response = agentic_ai(user_query)
        st.markdown(
            f"<div style='padding: 10px; background: #1e1e1e; color: white; border-radius: 5px;'>{response}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.warning("Please enter a question about the weather.")
