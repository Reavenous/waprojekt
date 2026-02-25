from flask import Flask, jsonify, request, make_response
import json

app = Flask(__name__)


def load_data():
    with open('db.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers['X-Server-ID'] = '1'
    return response


@app.route('/animals', methods=['GET'])
def get_all_animals():
    data = load_data()
    return create_response(data['animals'])


@app.route('/animals/<int:id>', methods=['GET'])
def get_animal(id):
    data = load_data()
    animal = next((a for a in data['animals'] if a['id'] == id), None)
    return create_response(animal) if animal else create_response({"error": "Not found"}, 404)

# curl -i -X POST http://localhost:8001/animals -H "Content-Type: application/json" -d "{\"species\": \"ovce\", \"breed\": \"Merino\", \"birthDate\": \"2024-02-01\", \"registered\": true}"
@app.route('/animals', methods=['POST'])
def create_animal():
    data = load_data()
    new_animal = request.json
    new_id = max(a['id'] for a in data['animals']) + 1 if data['animals'] else 1
    new_animal['id'] = new_id
    data['animals'].append(new_animal)
    save_data(data)
    return create_response(new_animal, 201)

# curl -i -X PATCH http://localhost:8001/animals/1 -H "Content-Type: application/json" -d "{\"registered\": false}"
@app.route('/animals/<int:id>', methods=['PUT', 'PATCH'])
def update_animal(id):
    data = load_data()
    animal = next((a for a in data['animals'] if a['id'] == id), None)
    if not animal:
        return create_response({"error": "Not found"}, 404)

    update_data = request.json
    animal.update(update_data)
    save_data(data)
    return create_response(animal)


if __name__ == '__main__':
    app.run(port=8001, debug=True)