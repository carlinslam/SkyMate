from flask import Flask, request, jsonify
import requests
import datetime
from cryptography.fernet import Fernet
from dateutil import parser
import os

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)  # ✅ Missing this before defining any routes

@app.route("/")         # ✅ This fixes the "Not Found" error on root
def home():
    return "Welcome to SkyMate – Flight Tracker API"

# Secure key for demo (store safely in production)
key = Fernet.generate_key()
cipher = Fernet(key)

@app.route('/track_flight', methods=['GET'])
def track_flight():
    flight_number = request.args.get('flight')
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_iata={flight_number}"

    response = requests.get(url)
    data = response.json()

    # Filter out any results without a valid estimated departure
    flights = data.get("data", [])
    valid_flights = [
        f for f in flights
        if f.get("departure", {}).get("estimated")
    ]

    if not valid_flights:
        return jsonify({"error": "Flight not found"}), 404

    # Pick the most recent one
    flight_info = valid_flights[0]
    departure_time = flight_info['departure']['estimated']
    time_left = calculate_time_left(departure_time)

    return jsonify({
        "flight": flight_number,
        "departure": departure_time,
        "time_until_departure": time_left
    })


def calculate_time_left(departure_time):
    now = datetime.datetime.utcnow()
    dt = parser.isoparse(departure_time)
    delta = dt - now
    return str(delta)

@app.route('/upload_pass', methods=['POST'])
def upload_pass():
    content = request.json.get("content")
    encrypted = cipher.encrypt(content.encode())
    return jsonify({"encrypted_pass": encrypted.decode()})

@app.route('/decrypt_pass', methods=['POST'])
def decrypt_pass():
    encrypted = request.json.get("encrypted_pass")
    decrypted = cipher.decrypt(encrypted.encode())
    return jsonify({"decrypted_pass": decrypted.decode()})

if __name__ == '__main__':
    app.run(debug=True)
