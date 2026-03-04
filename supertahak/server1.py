from flask import Flask, jsonify, request
from html import escape # NUTNÉ PRO SANITIZACI
import json

app = Flask(__name__)

#  HELPERS 
def load_data():
    with open("db.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sanitize_dict(d):
    return {k: escape(v) if isinstance(v, str) else v for k, v in d.items()}

#  GET ALL 
@app.route("/protocols", methods=["GET"])   # 🟡 ZDE ZMĚŇ
def get_all():
    data = load_data()
    records = data["protocols"]   # 🟡 ZDE ZMĚŇ
    
    # 🔵 FILTR (smazat tyto 3 řádky, pokud zadání filtr nechce)
    filter_val = request.args.get("status") # 🟡 ZDE ZMĚŇ "status" na slovo ze zadání
    if filter_val:
        records = [r for r in records if str(r.get("status")) == str(filter_val)] # 🟡 ZDE ZMĚŇ "status"
    
    response = jsonify(records)   
    response.headers["X-Server-ID"] = "1"
    return response

#  GET ONE 
@app.route("/protocols/<int:id>", methods=["GET"])   # 🟡 ZDE ZMĚŇ
def get_one(id):
    data = load_data()
    record = next((r for r in data["protocols"] if r["id"] == id), None)   # 🟡 ZDE ZMĚŇ
    if record is None:
        response = jsonify({"error": "Not found"})
        response.headers["X-Server-ID"] = "1"
        return response, 404
    response = jsonify(record)
    response.headers["X-Server-ID"] = "1"
    return response

#  POST CREATE 
@app.route("/protocols", methods=["POST"])   # 🟡 ZDE ZMĚŇ
def create():
    data = load_data()
    new_record = sanitize_dict(request.json)
    new_record["id"] = max((r["id"] for r in data["protocols"]), default=0) + 1   # 🟡 ZDE ZMĚŇ
    data["protocols"].append(new_record)   # 🟡 ZDE ZMĚŇ
    save_data(data)
    response = jsonify(new_record)
    response.headers["X-Server-ID"] = "1"
    return response, 201

#  PUT / PATCH UPDATE (🔵 Použij pouze pokud chtějí úpravu záznamu) 
@app.route("/protocols/<int:id>", methods=["PUT", "PATCH"])  # 🟡 ZDE ZMĚŇ
def update(id):
    data = load_data()
    record = next((r for r in data["protocols"] if r["id"] == id), None) # 🟡 ZDE ZMĚŇ
    if record is None:
        response = jsonify({"error": "Not found"})
        response.headers["X-Server-ID"] = "1"
        return response, 404
    updates = sanitize_dict(request.json)
    updates.pop("id", None)
    record.update(updates)
    save_data(data)
    response = jsonify(record)
    response.headers["X-Server-ID"] = "1"
    return response

#  DELETE (🔵 Použij pouze pokud chtějí smazání záznamu) 
@app.route("/protocols/<int:id>", methods=["DELETE"])  # 🟡 ZDE ZMĚŇ
def delete(id):
    data = load_data()
    original_len = len(data["protocols"])  # 🟡 ZDE ZMĚŇ
    data["protocols"] = [r for r in data["protocols"] if r["id"] != id] # 🟡 ZDE ZMĚŇ
    if len(data["protocols"]) == original_len: # 🟡 ZDE ZMĚŇ
        response = jsonify({"error": "Not found"})
        response.headers["X-Server-ID"] = "1"
        return response, 404
    save_data(data)
    response = app.response_class(status=204)
    response.headers["X-Server-ID"] = "1"
    return response

if __name__ == "__main__":
    app.run(port=8001, debug=True)