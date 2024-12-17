from flask import Flask, render_template, jsonify
import random  # Replace with real scraping logic
import requests
from bs4 import BeautifulSoup
import re  # Import regex library


def fetch_gaza_casualty_data():
    url = "https://www.aljazeera.com/news/longform/2023/10/9/israel-hamas-war-in-maps-and-charts-live-tracker"  # Replace with actual URL
    headers = {"User-Agent": "Mozilla/5.0"}  # Mimic browser request

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Locate the specific div containing casualty data
            casualty_div = soup.find("div", class_="wysiwyg css-1kw180w")
            if not casualty_div:
                print("Casualty data not found.")
                return None

            # Extract the first <ul> list under this div
            casualty_list = casualty_div.find("ul")
            if not casualty_list:
                print("No casualty list found.")
                return None

            # Parse the <li> items for data
            casualty_items = casualty_list.find_all("li")
            killed = injured = missing = 0  # Initialize values

            for item in casualty_items:
                text = item.get_text(strip=True)
                # Use regex to extract the first integer in the text
                number_match = re.search(r"(\d{1,3}(?:,\d{3})*|\d+)", text)  # Matches numbers with commas
                if number_match:
                    number = int(number_match.group(0).replace(",", ""))  # Clean commas
                    if "Killed" in text:
                        killed = number
                    elif "Injured" in text:
                        injured = number
                    elif "Missing" in text:
                        missing = number

            return {
                "killed": killed,
                "injured": injured,
                "missing": missing
            }
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

app = Flask(__name__)

# Route to serve the HTML file
@app.route('/')
def home():
    return render_template('index.html')

# API route to get the updated deaths
@app.route('/get-deaths')
def get_deaths():
    data = fetch_gaza_casualty_data()
    if data:
        return jsonify(data)
    # Fallback values
    return jsonify({'killed': 45059, 'injured': 107041, 'missing': 11000})

if __name__ == '__main__':
    app.run(debug=True)
