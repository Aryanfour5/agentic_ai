# 🌤 Weather Chatbot

## Overview
The **Weather Chatbot** is an AI-powered weather assistant that provides real-time weather updates and farming recommendations based on user queries. Leveraging **Google Gemini AI**, **OpenWeather API**, and **Streamlit**, the chatbot can understand weather-related questions, extract city names, fetch live weather data, and suggest farming decisions.

## Features
✅ **AI-Powered Understanding** - Uses Google Gemini AI to analyze and interpret user queries.  
✅ **Real-Time Weather Updates** - Fetches current weather data for any city using the OpenWeather API.  
✅ **Farming Recommendations** - Evaluates weather conditions for farming, offering insights for crops like tomatoes and corn.  
✅ **Multi-City Weather Insights** - Supports simultaneous weather checks for multiple cities.  
✅ **Proactive Notifications** - Sends daily weather alerts to users at scheduled times.  
✅ **Optimized Performance** - Uses multi-threading for parallel data fetching, ensuring speed and efficiency.

## Tech Stack
- **Python** - Core programming language
- **Google Gemini AI** - Natural language processing and query analysis
- **OpenWeather API** - Real-time weather data
- **Streamlit** - Interactive UI for user engagement
- **ThreadPoolExecutor** - Multithreading for faster API calls
- **Schedule** - Background scheduling for proactive weather alerts
- **Logging** - Enhanced debugging and monitoring

## Installation & Setup
### Prerequisites
Ensure you have **Python 3.8+** installed. Install dependencies with:
```sh
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file and set your API keys:
```
GOOGLE_API_KEY=your_google_gemini_api_key
WEATHER_API_KEY=your_openweather_api_key
```

### Running the Application
Run the chatbot using:
```sh
streamlit run app.py
```

## Usage
1. Open the web interface.
2. Enter a weather-related query (e.g., *"What's the weather like in New York?"*).
3. The chatbot processes the query, extracts location(s), and fetches weather data.
4. If farming-related, it evaluates weather conditions for crops.
5. View real-time insights and recommendations on the UI.

## Proactive Weather Alerts
- The chatbot runs a scheduled task every day at 8 AM (adjustable in `schedule.every().day.at("08:00")`).
- It fetches weather updates for predefined cities and sends alerts.

## Future Enhancements
🔹 **Machine Learning** - Self-learning capabilities for better recommendations.  
🔹 **Voice Integration** - Adding voice-based queries and responses.  
🔹 **More Crop Support** - Expanding farming advice to additional crops.  
🔹 **User Profiles** - Storing past queries for personalized recommendations.

## Screenshots
🚀 *Add screenshots of your UI here to make it visually appealing!*

## Contributing
Contributions are welcome! Feel free to fork this repo and submit pull requests.


---
👨‍💻 **Created by Aryan Bachute**

