from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Proměnná pro počítání požadavků, abychom zvládli sekvenci 2:3
request_counter = 0

def get_target():
    global request_counter
    # Modulo 5 zajistí cyklus 0, 1, 2, 3, 4
    position = request_counter % 5
    request_counter += 1
    
    # Pozice 0 a 1 -> Server 1 (Python)
    if position < 2:
        return "http://localhost:8001", "1"
    # Pozice 2, 3, 4 -> Server 2 (JS)
    else:
        return "http://localhost:8002", "2"

def forward_request(path):
    target_url, server_id = get_target()
    full_url = f"{target_url}/{path}"
    
    try:
        # Použijeme univerzální requests.request pro propuštění jakékoliv metody
        # params=request.args zajistí přenos query parametrů (např. ?status=completed)
        resp = requests.request(
            method=request.method,
            url=full_url,
            json=request.json if request.is_json else None,
            params=request.args 
        )
        
        # Sestavíme odpověď pro klienta
        response = Response(
            response=resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
        # Vrátíme hlavičku, kterou nám poslal cílový server
        response.headers['X-Server-ID'] = resp.headers.get('X-Server-ID', server_id)
        return response
        
    except requests.exceptions.ConnectionError:
        return Response(f"Server {server_id} neodpovida", status=503)

# Zachytíme všechny cesty pro entitu protocols
@app.route('/protocols', methods=['GET', 'POST'])
def handle_protocols():
    return forward_request('protocols')

@app.route('/protocols/<int:id>', methods=['GET', 'DELETE'])
def handle_protocol_id(id):
    return forward_request(f'protocols/{id}')

if __name__ == '__main__':
    print("Router (Load Balancer) bezi na portu 8000")
    app.run(port=8000)