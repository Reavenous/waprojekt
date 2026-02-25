from flask import Flask, jsonify, request, Response
import requests

app = Flask(__name__)

SERVERS = {
    1: "http://localhost:8001",
    2: "http://localhost:8002"
}

request_counter = 0

def get_target_server():
    global request_counter
    request_counter += 1

    if request_counter % 2 == 0:
        return SERVERS[2], 2
    else:
        return SERVERS[1], 1

def forward_request(endpoint):
    target_url, server_id = get_target_server()
    full_url = f"{target_url}/{endpoint}"

    try:
        if request.method == 'GET':
            resp = requests.get(full_url)
        elif request.method == 'POST':
            resp = requests.post(full_url, json=request.json)
        elif request.method in ['PUT', 'PATCH']:
            resp = requests.patch(full_url, json=request.json) if request.method == 'PATCH' else requests.put(full_url, json=request.json)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        response = Response(
            response=resp.content,
            status=resp.status_code,
            mimetype='application/json'
        )

        response.headers['X-Server-ID'] = str(server_id)

        return response

    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Server {server_id} is not responding"}), 503

@app.route('/animals', methods=['GET', 'POST'])
def handle_animals():
    return forward_request('animals')

@app.route('/animals/<int:id>', methods=['GET', 'PUT', 'PATCH'])
def handle_animal_id(id):
    return forward_request(f'animals/{id}')

if __name__ == '__main__':
    print("Router runs on port 8000")
    app.run(port=8000, debug=True)