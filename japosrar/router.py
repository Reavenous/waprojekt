from flask import Flask, request, Response
import requests

app = Flask(__name__)
request_counter = 0

SERVERS = [
    ("http://localhost:8001", "1"),
    ("http://localhost:8002", "2")
]

# Povolíme všechny metody, které potřebujeme (včetně PATCH pro úpravu)
@app.route('/socks', methods=['GET', 'POST'])
@app.route('/socks/<int:id>', methods=['GET', 'PATCH', 'PUT'])
def handle_request(id=None):
    global request_counter
    
    # Round Robin - čisté střídání 0 a 1 (1:1)
    primary_idx = request_counter % 2
    secondary_idx = (request_counter + 1) % 2
    request_counter += 1

    # Sestavení správné cesty
    path = 'socks' if id is None else f'socks/{id}'

    # 1. POKUS: Pošleme to na server, který je zrovna na řadě
    target_url, server_id = SERVERS[primary_idx]
    try:
        return forward_request(target_url, path, server_id)
    except requests.exceptions.ConnectionError:
        # FAILOVER: První server je mrtvý. Zkusíme automaticky ten druhý!
        target_url, server_id = SERVERS[secondary_idx]
        try:
            return forward_request(target_url, path, server_id)
        except requests.exceptions.ConnectionError:
            # Oba servery jsou nedostupné
            return Response("Service Unavailable", status=503)

def forward_request(base_url, path, server_id):
    full_url = f"{base_url}/{path}"
    
    resp = requests.request(
        method=request.method,
        url=full_url,
        json=request.json if request.is_json else None,
        params=request.args 
    )
    
    response = Response(
        response=resp.content,
        status=resp.status_code,
        content_type=resp.headers.get('Content-Type', 'application/json')
    )
    response.headers['X-Server-ID'] = resp.headers.get('X-Server-ID', server_id)
    return response

if __name__ == '__main__':
    print("Router bezi na portu 8000 s Failoverem")
    app.run(port=8000)