from flask import Flask, request, Response
import requests
app = Flask(__name__)

# ── STEP 1: CHANGE THIS ONE LINE to match your exam ──────────────────────
counter = 0
SEQUENCE = ["js","py","py","py"]   # ◄ CHANGE: see table above   ◄ CHANGE THIS

SERVERS = { "py": "http://localhost:8001", "js": "http://localhost:8002" }

def get_target():
    global counter
    target = SEQUENCE[counter % len(SEQUENCE)]
    # len(SEQUENCE) = 2 for Round Robin, 5 for 2:3, 4 for 1:3
    # counter % len cycles forever:  0,1,2,3,4,0,1,2,3,4 ...
    counter += 1
    return SERVERS[target]

# ── STEP 2: forward function  (never change this) ────────────────────────
# takes the request, sends to chosen server, returns the response
def forward(path):
    url = get_target() + path
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

# ── STEP 3: routes – change "protocols" to your entity name ─────────────
@app.route("/games", methods=["GET","POST"])  
# ^^^ add "PUT" to methods if exam has update without an id in URL
def collection():
    return forward("/games")   

@app.route("/games/<int:id>", methods=["GET","PUT","DELETE"])   
# ^^^ remove "DELETE" if no delete, remove "PUT" if no update
def single(id):
    return forward(f"/games/{id}")   

# ── START  (never change) ────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(port=8000, debug=True)