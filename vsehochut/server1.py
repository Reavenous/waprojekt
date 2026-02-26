from flask import Flask, jsonify, request
from html import escape # Ochrana (sanitizace) [cite: 210, 277]
import json

app = Flask(__name__)

def load_data():
    with open('db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sanitize_dict(d):
    # Vyčistí text od nebezpečných HTML znaků [cite: 210, 277]
    return {k: escape(v) if isinstance(v, str) else v for k, v in d.items()}

@app.after_request
def add_header(response):
    response.headers['X-Server-ID'] = '1' # Povinná hlavička [cite: 138, 205]
    return response

@app.route('/items', methods=['GET'])
def get_all():
    data = load_data()['items']
    
    # UNIVERZÁLNÍ FILTR (Filtruje podle čehokoliv, co přijde v URL)
    # Příklad: ?status=active nebo ?category=VIP
    for key, value in request.args.items():
        data = [i for i in data if str(i.get(key)) == str(value)]
        
    return jsonify(data), 200

@app.route('/items/<int:id>', methods=['GET'])
def get_one(id):
    item = next((i for i in load_data()['items'] if i['id'] == id), None)
    return (jsonify(item), 200) if item else (jsonify({"error": "Not found"}), 404)

@app.route('/items', methods=['POST'])
def create():
    db = load_data()
    new_item = sanitize_dict(request.json) # Vyčistíme vstup! [cite: 210, 277]
    new_item['id'] = max((i['id'] for i in db['items']), default=0) + 1 # Ignoruje ID a dá vlastní [cite: 139, 206]
    db['items'].append(new_item)
    save_data(db)
    return jsonify(new_item), 201

# --- ÚPRAVA ZÁZNAMU (PATCH/PUT) [cite: 188, 256] ---
@app.route('/items/<int:id>', methods=['PATCH', 'PUT']) 
def update(id):
    db = load_data()
    item = next((i for i in db['items'] if i['id'] == id), None)
    if not item: return jsonify({"error": "Not found"}), 404
    item.update(sanitize_dict(request.json))
    save_data(db)
    return jsonify(item), 200

# --- SMAZÁNÍ ZÁZNAMU (DELETE) [cite: 115, 140] ---
@app.route('/items/<int:id>', methods=['DELETE']) 
def delete(id):
    db = load_data()
    item = next((i for i in db['items'] if i['id'] == id), None)
    if not item: return jsonify({"error": "Not found"}), 404
    db['items'].remove(item)
    save_data(db)
    return '', 204 # Vrací 204 No Content [cite: 140]

if __name__ == '__main__':
    app.run(port=8001)