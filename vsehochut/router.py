from flask import Flask, request, Response
import requests

app = Flask(__name__)
request_counter = 0

SERVERS = [
    ("http://localhost:8001", "1"), # Index 0 = Python
    ("http://localhost:8002", "2")  # Index 1 = JS
]

def get_target():
    global request_counter
    pos = request_counter
    request_counter += 1
    
    # === VYBER SI BALANCING (ODKOMENTUJ POUZE JEDEN) ===
    
    # 1. Round Robin (1:1)
    idx = pos % 2
    
    # 2. Ratio 2:3 (Python:JS) [cite: 149]
    # idx = 0 if (pos % 5) < 2 else 1
    
    # 3. Ratio 1:3 (JS:Python) [cite: 283, 347]
    # idx = 1 if (pos % 4) == 0 else 0
    
    # ===================================================

    return SERVERS[idx], SERVERS[(idx + 1) % 2]

# Povolili jsme úplně všechny metody!
@app.route('/items', methods=['GET', 'POST'])
@app.route('/items/<int:id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def handle_request(id=None):
    path = 'items' if id is None else f'items/{id}'
    primary, secondary = get_target()

    # FAILOVER OCHRANA PROTI PÁDU
    try:
        return forward_request(primary[0], path, primary[1])
    except requests.exceptions.ConnectionError:
        try:
            return forward_request(secondary[0], path, secondary[1])
        except requests.exceptions.ConnectionError:
            return Response("Service Unavailable", status=503)

def forward_request(base_url, path, server_id):
    resp = requests.request(
        method=request.method,
        url=f"{base_url}/{path}",
        json=request.json if request.is_json else None,
        params=request.args 
    )
    response = Response(resp.content, resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    response.headers['X-Server-ID'] = resp.headers.get('X-Server-ID', server_id) # Hlavičky musí být [cite: 138, 205]
    return response

if __name__ == '__main__':
    app.run(port=8000)