"""
Server 1 - Python Flask Server pro správu nápojového lístku
Port: 8001
"""
from flask import Flask, jsonify, request, abort
import json
import os

app = Flask(__name__)
DB_FILE = 'db.json'


def load_data():
    if not os.path.exists(DB_FILE):
        return {"drinks": []}
    with open(DB_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    data = load_data()
    return jsonify({"drinks": data['drinks'], "server": 1})

@app.route('/drinks/<int:id>', methods=['GET'])
def get_drink(id):
    data = load_data()
    drink = next((d for d in data['drinks'] if d['id'] == id), None)
    if not drink:
        return jsonify({"error": "Drink not found", "server": 1}), 404
    return jsonify({**drink, "server": 1})

@app.route('/drinks', methods=['POST'])
def create_drink():
    if not request.json or 'name' not in request.json:
        return jsonify({"error": "Drink name missing", "server": 1}), 400

    data = load_data()
    new_drink = request.json

    new_id = max([drink['id'] for drink in data['drinks']], default=0) + 1
    new_drink['id'] = new_id

    if 'available' not in new_drink:
        new_drink['available'] = True

    data['drinks'].append(new_drink)
    save_data(data)
    return jsonify({**new_drink, "server": 1}), 201

@app.route('/drinks/<int:id>', methods=['PUT'])
def update_drink(id):
    data = load_data()
    drink = next((d for d in data['drinks'] if d['id'] == id), None)

    if not drink:
        return jsonify({"error": "Drink not found", "server": 1}), 404

    if not request.json:
        return jsonify({"error": "No data for update", "server": 1}), 400

    update_data = request.json
    for key, value in update_data.items():
        if key != 'id':
            drink[key] = value

    save_data(data)
    return jsonify({**drink, "server": 1})


if __name__ == '__main__':
    print("Server 1 (Python) runs on port 8001")
    app.run(port=8001, debug=True)