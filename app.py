import streamlit as st
from dotenv import load_dotenv
import os
import geocoder
import googlemaps
from math import radians, sin, cos, sqrt, atan2

# Load environment variables
load_dotenv()
google_maps_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=google_maps_api_key)

# Haversine Formula for distance (in KM)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

# Get coordinates from text or auto location
def get_coordinates(location_text):
    if location_text.lower() == "auto":
        g = geocoder.ip("me")
        if g.ok:
            return g.latlng
        else:
            st.error("Could not detect location automatically.")
            return None
    else:
        geocode_result = gmaps.geocode(location_text)
        if geocode_result:
            loc = geocode_result[0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        else:
            st.error("Invalid location input.")
            return None

# Search places from Google Maps API
def search_food_places(food, location, distance_km):
    places_result = gmaps.places_nearby(
        location=location,
        radius=distance_km * 1000,
        keyword=food,
        type="restaurant"
    )
    return places_result.get("results", [])

# Format each restaurant output
def format_place(place, user_lat, user_lng):
    name = place.get("name")
    rating = place.get("rating", "N/A")
    loc = place["geometry"]["location"]
    maps_url = f"https://www.google.com/maps/search/?api=1&query={loc['lat']},{loc['lng']}"
    distance = calculate_distance(user_lat, user_lng, loc["lat"], loc["lng"])
    return f"**{name}**\n⭐ Rating: {rating}\n📍 [View on Map]({maps_url})\n🛣️ Distance: {distance} km\n"

# --- Streamlit UI ---
st.title("🍽️ AI-Powered Restaurant Recommender")

with st.form("input_form"):
    food_query = st.text_input("What food do you want?", placeholder="e.g., biryani, dosa")
    location_input = st.text_input("Enter your location (or type 'auto')", placeholder="e.g., Chennai or auto")
    distance_km = st.slider("Search within distance (km):", 1, 20, 5)
    submitted = st.form_submit_button("Search")

if submitted:
    coords = get_coordinates(location_input)
    if coords:
        user_lat, user_lng = coords
        with st.spinner("🔍 Finding top restaurants..."):
            places = search_food_places(food_query, coords, distance_km)
            if not places:
                st.warning("No restaurants found. Try changing the location or food.")
            else:
                for place in places:
                    st.markdown(format_place(place, user_lat, user_lng))
