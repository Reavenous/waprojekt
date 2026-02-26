from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Tato proměnná počítá, kolikátý dotaz už přišel. Podle ní střídáme servery.
request_counter = 0

# Zde definujeme naše dva servery. 
# Index 0 je Python (port 8001), Index 1 je JavaScript (port 8002).
SERVERS = [
    ("http://localhost:8001", "1"), 
    ("http://localhost:8002", "2")  
]

def get_target():
    global request_counter
    pos = request_counter
    request_counter += 1 # S každým dotazem se číslo zvětší o 1
    
    # --- ⚠️ ZDE VYBER SPRÁVNOU MATIKU PODLE ZADÁNÍ (ZBYTEK SMAŽ/ZAKOMENTUJ) ⚠️ ---
    
    # VARIANTA A: Round Robin (1:1) -> Střídá Python a JS přesně na střídačku
    idx = pos % 2
    
    # VARIANTA B: Ratio 2:3 (Python:JS) -> 2x Python, 3x JS
    # idx = 0 if (pos % 5) < 2 else 1
    
    # VARIANTA C: Ratio 1:3 (JS:Python) -> 1x JS, 3x Python
    # idx = 1 if (pos % 4) == 0 else 0
    
    # -----------------------------------------------------------------------------

    # Funkce vrací dva servery: první je ten, na který to chceme poslat (primární),
    # a druhý je ten záložní (sekundární), kdyby ten první spadnul.
    return SERVERS[idx], SERVERS[(idx + 1) % 2]


# --- ⚠️ ZMĚŇ SLOVO 'ENTITA' ZA NÁZEV ZE ZADÁNÍ (např. 'socks', 'tickets', 'animals') ⚠️ ---
@app.route('/ENTITA', methods=['GET', 'POST'])
@app.route('/ENTITA/<int:id>', methods=['GET', 'PATCH', 'PUT', 'DELETE']) # Povolili jsme všechny metody!
def handle_request(id=None):
    # Pokud není zadáno ID, cesta je jen /ENTITA. Pokud je zadáno, je to /ENTITA/1 atd.
    path = 'ENTITA' if id is None else f'ENTITA/{id}'
    
    # Získáme primární a sekundární server z naší funkce výše
    primary, secondary = get_target()

    # --- ⚠️ FAILOVER LOGIKA (Ochrana proti pádu serveru) ⚠️ ---
    try:
        # ZKUSÍME TO POSLAT NA PRIMÁRNÍ SERVER...
        return forward_request(primary[0], path, primary[1])
    except requests.exceptions.ConnectionError:
        # POKUD PRIMÁRNÍ NEODPOVÍDÁ (SPADL), AUTOMATICKY TO ZKUSÍME POSLAT NA SEKUNDÁRNÍ...
        try:
            return forward_request(secondary[0], path, secondary[1])
        except requests.exceptions.ConnectionError:
            # POKUD SPADLY OBA DVA, VRÁTÍME CHYBU 503 SERVICE UNAVAILABLE
            return Response("Service Unavailable", status=503)

# Tato funkce jen vezme dotaz od klienta a beze změny ho přepošle na cílový server
def forward_request(base_url, path, server_id):
    resp = requests.request(
        method=request.method,
        url=f"{base_url}/{path}",
        json=request.json if request.is_json else None,
        params=request.args # Tímto se předávají parametry pro filtr (např. ?color=red)
    )
    # Sestavíme odpověď pro klienta zpět
    response = Response(resp.content, resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    # Přidáme povinnou hlavičku X-Server-ID
    response.headers['X-Server-ID'] = resp.headers.get('X-Server-ID', server_id)
    return response

if __name__ == '__main__':
    app.run(port=8000)