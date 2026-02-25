from flask import Flask, jsonify, request
import json

app = Flask(__name__)
DB_FILE = 'db.json'

def load_data():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/animals', methods=['GET'])
def get_animals():
    data = load_data()
    resp = jsonify(data['animals'])
    resp.headers['X-Server-ID'] = 1
    return resp

@app.route('/animals/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    data = load_data()
    animal = next((a for a in data['animals'] if a['id'] == animal_id), None)
    if not animal:
        return jsonify({"error": "Not found"}), 404

    resp = jsonify(animal)
    resp.headers['X-Server-ID'] = 1
    return resp

@app.route('/animals', methods=['POST'])
def create_animal():
    data = load_data()
    body = request.json or {}

    new_id = max(a['id'] for a in data['animals']) + 1 if data['animals'] else 1

    animal = {
        "id": new_id,
        "species": str(body.get("species", "")).strip(),
        "breed": str(body.get("breed", "")).strip(),
        "birthDate": body.get("birthDate", ""),
        "registered": bool(body.get("registered", False))
    }

    data['animals'].append(animal)
    save_data(data)

    resp = jsonify(animal)
    resp.status_code = 201
    resp.headers['X-Server-ID'] = 1
    return resp

@app.route('/animals/<int:animal_id>', methods=['PUT'])
def update_animal(animal_id):
    data = load_data()
    body = request.json or {}

    for animal in data['animals']:
        if animal['id'] == animal_id:
            animal.update({
                "species": body.get("species", animal["species"]),
                "breed": body.get("breed", animal["breed"]),
                "birthDate": body.get("birthDate", animal["birthDate"]),
                "registered": body.get("registered", animal["registered"])
            })
            save_data(data)
            resp = jsonify(animal)
            resp.headers['X-Server-ID'] = 1
            return resp

    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(port=8001, debug=True)