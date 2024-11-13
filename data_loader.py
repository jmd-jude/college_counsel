import requests
import json
import streamlit as st
from datetime import datetime

# Sample schools list
SAMPLE_SCHOOLS = [
    "Harvard University",
    "Yale University",
    "Princeton University",
    "Columbia University in the City of New York",
    "University of Pennsylvania",
    "Brown University",
    "Dartmouth College",
    "Cornell University",
    "University of California-Berkeley",
    "University of California-Los Angeles",
    "University of Michigan-Ann Arbor",
    "University of Virginia-Main Campus",
    "Georgia Institute of Technology-Main Campus",
    "University of North Carolina at Chapel Hill",
    "Williams College",
    "Amherst College",
    "Pomona College",
    "Swarthmore College",
    "Ohio State University-Main Campus",
    "Pennsylvania State University-Main Campus",
    "University of Texas at Austin",
    "University of Wisconsin-Madison",
    "University of Florida",
    "Arizona State University-Tempe",
]

@st.cache_data
def fetch_school_data():
    """Fetch and cache school data from the API"""
    API_KEY = st.secrets["API_KEY"]
    school_data = {}

    for school in SAMPLE_SCHOOLS:
        print(f"Collecting data for {school}...")
        params = {
            'api_key': API_KEY,
            'school.name': school,
            'per_page': 1
        }
        response = requests.get(
            'https://api.data.gov/ed/collegescorecard/v1/schools',
            params=params
        )

        if response.status_code == 200:
            data = response.json()
            if data['results']:
                school_data[school] = {
                    'id': data['results'][0]['id'],
                    'school_name': school,
                    'collected_at': datetime.now().isoformat(),
                    'raw_data': data['results'][0]
                }
    
    return school_data

if __name__ == "__main__":
    # This will still work locally for testing
    data = fetch_school_data()
    print(f"Collected data for {len(data)} schools")