from flask import Flask, request, jsonify
import requests
import datetime
from cryptography.fernet import Fernet
from dateutil import parser

app = Flask(__name__)
API_KEY = 'your_api_key_here'  # Replace with your AviationStack key

# Demo encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

@app.route('/track_flight', methods=['GET'])
def track_flight():
    flight_number = request.args.get('flight')
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_iata={flight_number}"

    response = requests.get(url)
    data = response.json()

    if 'data' not in data or not data['data']:
        return jsonify({"error": "Flight not found"}), 404

    flight_info = data['data'][0]
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
