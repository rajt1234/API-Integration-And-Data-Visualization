# === Importing required libraries ===
import streamlit as st                                # Build web app UI
import requests                                       # Fetch data from APIs
import pandas as pd                                   # Handle tabular data
import matplotlib.pyplot as plt                       # Create basic plots
import seaborn as sns                                 # Enhanced statistical plots
import numpy as np                                    # Numerical operations
import folium                                         # Create interactive maps
from streamlit_folium import folium_static            # Display folium map in Streamlit
from matplotlib.colors import LinearSegmentedColormap # Custom color gradients
from matplotlib.patches import Patch                  # Custom legend boxes
from matplotlib.lines import Line2D                   # Custom legend lines
from dotenv import load_dotenv                        # To load API keys and environment variables from a `.env` file.
import os                                             # To access environment variables and system functions.

load_dotenv()   # I used this command to load environment variables from a .env file into my python environment.

# === Setting up Streamlit page settings ===
st.set_page_config(layout="wide", page_title="Visualized Weather Dashboard")
st.title("🌤️ Visualized Weather Dashboard")

# === Enter your city name. I set default city as Delhi, you can change city after running the code. ===
city = st.text_input("Enter your city:", "Delhi").capitalize()
api_key = os.getenv("OpenWeatherMap_API")  # Replace with your actual OpenWeatherMap API key

# === Fetching current weather data from OpenWeatherMap ===
url_current = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
res_current = requests.get(url_current)

if res_current.status_code == 200:
    data = res_current.json()

# === Extracting important weather parameters ===
    weather_data = {
        "City": data["name"],
        "Country": data["sys"]["country"],
        "Longitude": data["coord"]["lon"],
        "Latitude": data["coord"]["lat"],
        "Temperature (°C)": data["main"]["temp"],
        "Feels Like (°C)": data["main"]["feels_like"],
        "Min Temp (°C)": data["main"]["temp_min"],
        "Max Temp (°C)": data["main"]["temp_max"],
        "Pressure (hPa)": data["main"]["pressure"],
        "Humidity (%)": data["main"]["humidity"],
        "Weather": data["weather"][0]["main"],
        "Description": data["weather"][0]["description"],
        "Wind Speed (m/s)": data["wind"]["speed"],
        "Wind Direction (°)": data["wind"]["deg"],
        "Cloudiness (%)": data["clouds"]["all"],
        "Visibility (m)": data["visibility"]
    }
    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

# === Displaying weather data in a table ===
    df = pd.DataFrame(list(weather_data.items()), columns=["Parameter", "Value"])
    st.subheader("📋 Current Weather Data")
    st.dataframe(df, use_container_width=True)

# === Fetching and visualizing 5-day forecast ===
    st.markdown("## 📈 5-Day Weather Forecast")
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    forecast_response = requests.get(forecast_url)

    if forecast_response.status_code == 200:
        forecast = forecast_response.json()
        forecast_df = pd.DataFrame(forecast['list'])
        forecast_df['dt_txt'] = pd.to_datetime(forecast_df['dt_txt'])
        forecast_df['Temperature'] = forecast_df['main'].apply(lambda x: x['temp'])

# === Line plot of temperature forecast ===
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.lineplot(x=forecast_df['dt_txt'], y=forecast_df['Temperature'], marker='o', color="teal")
        plt.title(f"5-Day Forecast Temperature Trend in {city}", fontsize=14, weight='bold')
        plt.xticks(rotation=45)
        plt.ylabel("Temp (°C)")
        plt.tight_layout()
        st.pyplot(fig)

# === Creating 3 side-by-side visualizations (row 1) ===
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🌡️ Weather Parameters")
        # Filter and plot important parameters
        plot_data = df[df['Parameter'].isin([
            'Temperature (°C)', 'Feels Like (°C)', 'Pressure (hPa)', 'Humidity (%)',
            'Wind Speed (m/s)', 'Wind Direction (°)', 'Visibility (m)', 'Cloudiness (%)'
        ])]
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.barplot(data=plot_data, x='Parameter', y='Value', palette='coolwarm')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown("### 📊 Parameters Comparison")
        # Filter numeric parameters and plot
        plot_df = df[df["Value"].apply(lambda x: isinstance(x, (int, float)))]
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.barplot(data=plot_df, y="Parameter", x="Value", palette="mako")
        plt.tight_layout()
        st.pyplot(fig)

    with col3:
        st.markdown("### 🔥 Heatmap of Weather Data")
         # Create and display a heatmap of selected data
        heat_dict = {
            "Temperature (°C)": data["main"]["temp"],
            "Feels Like (°C)": data["main"]["feels_like"],
            "Pressure (hPa)": data["main"]["pressure"],
            "Humidity (%)": data["main"]["humidity"],
            "Visibility (m)": data["visibility"],
            "Wind Speed (m/s)": data["wind"]["speed"],
            "Wind Direction (°)": data["wind"]["deg"],
            "Cloudiness (%)": data["clouds"]["all"]
        }
        heat_df = pd.DataFrame.from_dict(heat_dict, orient='index', columns=['Value'])
        custom_cmap = LinearSegmentedColormap.from_list("custom", ["#3498db", "#f1c40f", "#e67e22", "#e74c3c"])
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.heatmap(heat_df, annot=True, cmap=custom_cmap, fmt=".1f", linewidths=1, linecolor='white')
        plt.xticks([])
        plt.tight_layout()
        st.pyplot(fig)

# === Creating 3 more visualizations (row 2) ===
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("### 🌬️ Wind Speed & Direction")
         # Convert wind direction to polar angle and plot
        wind_speed_mps = data["wind"]["speed"]
        wind_deg = data["wind"]["deg"]
        theta = np.deg2rad(wind_deg)

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'polar': True})
        ax.bar(theta, wind_speed_mps, width=np.deg2rad(10), color="orangered", alpha=0.8, edgecolor='black')

         # Configure polar plot directions
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlabel_position(135)

        max_mps = int(np.ceil(wind_speed_mps)) + 2
        ax.set_rticks(range(0, max_mps + 1, 1))
        ax.set_yticklabels([f"{v} m/s" for v in range(0, max_mps + 1, 1)], fontsize=9)

         # Adding wind direction arrow
        ax.annotate('', xy=(theta, wind_speed_mps), xytext=(0, 0),
                    arrowprops=dict(facecolor='navy', edgecolor='white', width=2, headwidth=8))

         # Adding cardinal direction labels
        labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        angles = np.deg2rad(np.arange(0, 360, 45))
        label_radius = max_mps + 2
        for angle, label in zip(angles, labels):
            ax.text(angle, label_radius, label, ha='center', va='center',
                    fontsize=10, fontweight='bold', color='dimgray')

         # Making custom legend
        ax.legend(
            handles=[
                Patch(color='orangered', label='Wind Speed (m/s)'),
                Line2D([0], [0], color='navy', linewidth=2.5, marker='>', markersize=10,
                       label='Wind Direction', linestyle='-', markerfacecolor='navy')
            ],
            loc='upper right', bbox_to_anchor=(1.35, 1.1)
        )
        st.pyplot(fig)

    with col5:
        st.markdown("### 📈 Temperature vs Feels Like")
        # Line plot of actual vs feels like temperature
        x_labels = ["Actual Temp", "Feels Like"]
        y_values = [data["main"]["temp"], data["main"]["feels_like"]]
        fig, ax = plt.subplots(figsize=(4, 4))
        plt.plot(x_labels, y_values, marker='o', linestyle='-', color='teal')
        for i, v in enumerate(y_values):
            plt.text(i, v + 0.5, f'{v:.1f}°C', ha='center')
        plt.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

    with col6:
        st.markdown("### 🧪 Atmospheric Composition")
        # Pie chart for humidity, cloudiness, and visibility
        humidity = data["main"]["humidity"]
        cloudiness = data["clouds"]["all"]
        visibility_pct = min((data["visibility"] / 10000) * 100, 100)
        labels = ['Humidity', 'Cloudiness', 'Visibility']
        values = [humidity, cloudiness, visibility_pct]
        colors = ['skyblue', 'lightgray', 'lightgreen']
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
               wedgeprops=dict(width=0.4))
        st.pyplot(fig)

    # === Showing weather location map and emoji legend side-by-side ===
    st.markdown("## 🗺️ Weather Location Map & Weather Symbol Guide")

    col_map, col_legend = st.columns([2.5, 1.5])  # Adjusting width ratio

    with col_map:
        # Displaying current location on interactive map
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], popup=f"{city}: {weather_data['Weather']}",
                    icon=folium.Icon(color='blue', icon='cloud')).add_to(m)
        folium_static(m, width=600, height=450)

    with col_legend:
        # Showing emoji based on current weather
        weather_condition = data["weather"][0]["main"].lower()
        emoji_map = {
            "clear": "☀️",
            "clouds": "☁️",
            "rain": "🌧️",
            "drizzle": "🌦️",
            "thunderstorm": "⛈️",
            "snow": "❄️",
            "mist": "🌫️",
            "haze": "🌫️",
            "fog": "🌫️",
            "tornado": "🌪️"
        }
        emoji = emoji_map.get(weather_condition, "🌈")
        st.markdown(f"### Current Weather: {emoji}")

        # Emoji legend for different weather types
        st.markdown("### 🌈 Weather Symbol Guide")
        symbol_legend = {
            "☀️": "Clear Sky",
            "🌤️": "Few Clouds",
            "☁️": "Cloudy",
            "🌧️": "Rain",
            "⛈️": "Thunderstorm",
            "❄️": "Snow",
            "🌫️": "Mist / Fog",
            "🌪️": "Tornado",
        }
        for symbol, desc in symbol_legend.items():
            st.markdown(f"{symbol} — {desc}")
            
# === If API request fails, show error ===
else:
    st.error(f"❌ Failed to retrieve data. Status code: {res_current.status_code}")