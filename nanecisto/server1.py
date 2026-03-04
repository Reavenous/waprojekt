from flask import Flask, jsonify, request
import json
app = Flask(__name__)

# ── HELPERS  (never change) ──────────────────────────────────────────────
def load_data():
    with open("db.json", "r", encoding="utf-8") as f:
        return json.load(f)
def save_data(data):
    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── GET ALL ──────────────────────────────────────────────────────────────
@app.route("/games", methods=["GET"])   
def get_all():
    data = load_data()
    records = data["games"]   
    # --- filter block: delete these 3 lines if exam has no filter ---
    status_filter = request.args.get("category")   # change "category" and "status" to your filter name and field
    if status_filter:
        records = [r for r in records if r.get("category") == status_filter]
    # -------------------------------------------------------------------
    response = jsonify({"games": records, "server": 1})   
    response.headers["X-Server-ID"] = "1"
    return response

# ── GET ONE ──────────────────────────────────────────────────────────────
@app.route("/games/<int:id>", methods=["GET"])   
def get_one(id):
    data = load_data()
    record = next((r for r in data["games"] if r["id"] == id), None)   
    if record is None:
        response = jsonify({"error": "Not found"})
        response.headers["X-Server-ID"] = "1"
        return response, 404
    response = jsonify(record)
    response.headers["X-Server-ID"] = "1"
    return response

# ── POST CREATE ──────────────────────────────────────────────────────────
@app.route("/games", methods=["POST"])   
def create():
    data = load_data()
    new_record = request.json
    new_record["id"] = max((r["id"] for r in data["games"]), default=0) + 1   
    data["games"].append(new_record)   
    save_data(data)
    response = jsonify({**new_record, "server": 1})
    response.headers["X-Server-ID"] = "1"
    return response, 201
# ── PUT UPDATE  (only if exam asks for update) ────────────────────────────
@app.route("/games/<int:id>", methods=["PUT"])  # change "protocols"
def update(id):
    data = load_data()
    record = next((r for r in data["games"] if r["id"] == id), None)
    if record is None:
        response = jsonify({"error": "Not found"})
        response.headers["X-Server-ID"] = "1"
        return response, 404
    updates = request.json
    updates.pop("id", None)   # never overwrite the id!
    record.update(updates)
    save_data(data)
    response = jsonify({**record, "server": 1})
    response.headers["X-Server-ID"] = "1"
    return response



# ── START  (never change) ────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(port=8001, debug=True)