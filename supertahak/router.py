from flask import Flask, request, Response
import requests
app = Flask(__name__)

#  KROK 1: ZVOL SPRÁVNOU SEKVENCI (Odkomentuj jen jednu!) 
counter = 0

# Round Robin (1:1)
SEQUENCE = ["js","py"]   

# Ratio 2:3 (Python:JS)
# SEQUENCE = ["py","py","js","js","js"]

# Ratio 1:3 (JS:Python)
# SEQUENCE = ["js","py","py","py"]

SERVERS = { "py": "http://localhost:8001", "js": "http://localhost:8002" }

def get_targets():
    global counter
    primary = SEQUENCE[counter % len(SEQUENCE)]
    # Failover: Určí záložní server (ten druhý)
    secondary = "py" if primary == "js" else "js"
    counter += 1
    return SERVERS[primary], SERVERS[secondary]

#  KROK 2: FORWARD FUNKCE S FAILOVER OCHRANOU 
def forward(path):
    primary_url, secondary_url = get_targets()
    
    try:
        return make_request(primary_url + path)
    except requests.exceptions.ConnectionError:
        # POKUD PRIMÁRNÍ SERVER SPADL, ZKUSÍ ZÁLOŽNÍ
        try:
            return make_request(secondary_url + path)
        except requests.exceptions.ConnectionError:
            return Response("Service Unavailable", status=503)

def make_request(url):
    resp = requests.request(
        method  = request.method,
        url     = url,
        params  = request.args,
        json    = request.get_json(silent=True),
        headers = {"Content-Type": "application/json"}
    )
    response = Response(resp.content, status=resp.status_code)
    if "Content-Type" in resp.headers:
        response.headers["Content-Type"] = resp.headers["Content-Type"]
    if "X-Server-ID" in resp.headers:
        response.headers["X-Server-ID"] = resp.headers["X-Server-ID"]
    return response

#  KROK 3: ROUTY 
@app.route("/protocols", methods=["GET","POST"])  # 🟡 ZDE ZMĚŇ
def collection():
    return forward("/protocols")   # 🟡 ZDE ZMĚŇ

# Povoleny všechny metody: GET, PUT, PATCH i DELETE
@app.route("/protocols/<int:id>", methods=["GET","PUT","PATCH","DELETE"])  # 🟡 ZDE ZMĚŇ
def single(id):
    return forward(f"/protocols/{id}")   # 🟡 ZDE ZMĚŇ

if __name__ == "__main__":
    app.run(port=8000, debug=True)