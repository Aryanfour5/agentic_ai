import os
import json
import google.generativeai as genai
import requests
import logging
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Keys (Replace with your actual API keys)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


print("GOOGLE_API_KEY:", GOOGLE_API_KEY)  # Should print the actual key
print("WEATHER_API_KEY:", WEATHER_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


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
        return f"🌡 Temperature: {data['main']['temp']}°C | 💧 Humidity: {data['main']['humidity']}% | 🌬 Wind: {data['wind']['speed']} km/h"
    except:
        return "Weather data unavailable"


def agentic_ai(user_query):
    """Process the user query and return a response."""
    if not is_weather_related(user_query):
        return "❌ You don't need to know that. Ask about the weather."
    response = model.generate_content(
        f"Extract city names from this query and return them in JSON format as {{'cities': ['city1', 'city2', ...]}}. Query: '{user_query}'"
    )
    locations = extract_locations(response.text)
    if not locations:
        return "⚠ No valid locations found. Please ask about a specific city."
    with ThreadPoolExecutor(max_workers=len(locations)) as executor:
        results = {
            city: executor.submit(get_weather_details, city).result()
            for city in locations
        }
    return "\n".join([f"📍 {city}: {results[city]}" for city in results])


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
