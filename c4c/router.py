from flask import Flask, request, Response
import requests

app = Flask(__name__)

SERVERS = [
    {"url": "http://localhost:8001", "id": 1},
    {"url": "http://localhost:8002", "id": 2}
]

current = 0

def get_next_server():
    global current
    server = SERVERS[current]
    current = (current + 1) % len(SERVERS)
    return server

@app.route('/animals', methods=['GET', 'POST'])
@app.route('/animals/<int:animal_id>', methods=['GET', 'PUT'])
def proxy(animal_id=None):
    server = get_next_server()
    url = server["url"] + request.path

    resp = requests.request(
        method=request.method,
        url=url,
        json=request.get_json(silent=True)
    )

    response = Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get('Content-Type')
    )
    response.headers['X-Server-ID'] = server["id"]
    return response

if __name__ == '__main__':
    app.run(port=8000, debug=True)
