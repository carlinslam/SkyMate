from flask import Flask, request, jsonify
import requests
import datetime
from cryptography.fernet import Fernet
from dateutil import parser
import os

API_KEY ="0d23219465fa374940821a8400682d1a"
print("🔑 Loaded API_KEY:", API_KEY)  # Debugging line

if not API_KEY:
    raise RuntimeError("❌ API_KEY is missing! Make sure it's set in Render.")



# Secure key for demo (store safely in production)
key = Fernet.generate_key()
cipher = Fernet(key)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/track_flight', methods=['GET'])
def track_flight():
    flight_number = request.args.get('flight')

    if not flight_number:
        return jsonify({"error": "Missing 'flight' query parameter"}), 400

    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_iata={flight_number}"
    print(f"✈️ Fetching flight: {flight_number} from {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("❌ Error fetching flight data:", e)
        return jsonify({"error": "Flight API request failed"}), 500

    flights = data.get("data", [])
    valid_flights = [
        f for f in flights
        if f.get("departure", {}).get("estimated")
    ]

    if not valid_flights:
        return jsonify({"error": "Flight not found"}), 404

    flight_info = valid_flights[0]
    departure_time = flight_info['departure']['estimated']
    time_left = calculate_time_left(departure_time)

    return jsonify({
        "flight": flight_number,
        "departure": departure_time,
        "time_until_departure": time_left
    })



def calculate_time_left(departure_time):
    try:
        now = datetime.datetime.utcnow()
        dt = parser.isoparse(departure_time)
        delta = dt - now
        return str(delta)
    except Exception as e:
        print("❌ Error parsing time:", e)
        return "unknown"

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


