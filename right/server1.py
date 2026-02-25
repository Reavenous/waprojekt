from flask import Flask, jsonify, request, make_response
import json

app = Flask(__name__)

def load_data():
    with open('db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Tento kód automaticky přidá hlavičku X-Server-ID: 1 ke každé odpovědi
@app.after_request
def add_header(response):
    response.headers['X-Server-ID'] = '1'
    return response

@app.route('/protocols', methods=['GET'])
def get_protocols():
    data = load_data()
    protocols = data['protocols']
    
    # Filtrování podle statusu (pokud je v URL ?status=X)
    status_filter = request.args.get('status')
    if status_filter:
        protocols = [p for p in protocols if p['status'] == status_filter]
        
    return jsonify(protocols), 200

@app.route('/protocols/<int:id>', methods=['GET'])
def get_protocol(id):
    data = load_data()
    protocol = next((p for p in data['protocols'] if p['id'] == id), None)
    if protocol:
        return jsonify(protocol), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/protocols', methods=['POST'])
def create_protocol():
    data = load_data()
    new_protocol = request.json
    
    # Ignorujeme ID z požadavku a vytvoříme vlastní
    new_id = max((p['id'] for p in data['protocols']), default=0) + 1
    new_protocol['id'] = new_id
    
    data['protocols'].append(new_protocol)
    save_data(data)
    return jsonify(new_protocol), 201

@app.route('/protocols/<int:id>', methods=['DELETE'])
def delete_protocol(id):
    data = load_data()
    protocol = next((p for p in data['protocols'] if p['id'] == id), None)
    
    if not protocol:
        return jsonify({"error": "Not found"}), 404
        
    data['protocols'].remove(protocol)
    save_data(data)
    return '', 204 # 204 No Content při úspěchu

if __name__ == '__main__':
    app.run(port=8001)