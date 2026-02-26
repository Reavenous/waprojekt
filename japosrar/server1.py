from flask import Flask, jsonify, request, make_response
import json

app = Flask(__name__)

def load_data():
    with open('db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.after_request
def add_header(response):
    response.headers['X-Server-ID'] = '1'
    return response

@app.route('/socks', methods=['GET'])
def get_socks():
    data = load_data()
    socks = data['socks']
    
    # Filtrování podle barvy (?color=X)
    color_filter = request.args.get('color')
    if color_filter:
        socks = [p for p in socks if p.get('color') == color_filter]
        
    return jsonify(socks), 200

@app.route('/socks/<int:id>', methods=['GET'])
def get_sock(id):
    data = load_data()
    sock = next((p for p in data['socks'] if p['id'] == id), None)
    if sock:
        return jsonify(sock), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/socks', methods=['POST'])
def create_sock():
    data = load_data()
    new_sock = request.json
    
    new_id = max((p['id'] for p in data['socks']), default=0) + 1
    new_sock['id'] = new_id
    
    data['socks'].append(new_sock)
    save_data(data)
    return jsonify(new_sock), 201

# ÚPRAVA ZÁZNAMU MÍSTO MAZÁNÍ
@app.route('/socks/<int:id>', methods=['PATCH', 'PUT'])
def update_sock(id):
    data = load_data()
    sock = next((p for p in data['socks'] if p['id'] == id), None)
    
    if not sock:
        return jsonify({"error": "Not found"}), 404
        
    # Vezme původní data ponožky a aktualizuje je tím, co přišlo v requestu
    update_data = request.json
    sock.update(update_data) 
    save_data(data)
    
    return jsonify(sock), 200

if __name__ == '__main__':
    app.run(port=8001)