from flask import Flask, jsonify, request
from html import escape # Tento import potřebujeme pro sanitizaci!
import json

app = Flask(__name__)

# Otevře soubor db.json a načte z něj data
def load_data():
    with open('db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Zapíše upravená data zpět do souboru db.json
def save_data(data):
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- ⚠️ SANITIZACE VSTUPU (Ochrana před útokem) ⚠️ ---
# Projde všechna data, která nám poslal uživatel. Pokud je to text, převede nebezpečné
# značky jako <script> na bezpečný text, aby se nespustily. (např. jméno: Alexandre Basseville projde bez změny)
def sanitize_dict(d):
    return {k: escape(v) if isinstance(v, str) else v for k, v in d.items()}

# Automaticky přidá hlavičku X-Server-ID ke každé odpovědi
@app.after_request
def add_header(response):
    response.headers['X-Server-ID'] = '1'
    return response

# --- ⚠️ PŘEPIŠ 'ENTITA' (např. 'socks', 'tickets') VE VŠECH @app.route ZDE DOLE ⚠️ ---

@app.route('/ENTITA', methods=['GET'])
def get_all():
    # Načteme všechny záznamy z databáze (Nezapomeň přepsat 'ENTITA' i v závorce!)
    data = load_data()['ENTITA']
    
    # --- ⚠️ FILTROVÁNÍ (ZAPNI POUZE POKUD TO ZADÁNÍ VYŽADUJE) ⚠️ ---
    # Pokud učitel chce filtr, smaž křížky (#) u řádků níže a přepiš slovo 'color' 
    # na to, co vyžaduje zadání (např. 'status', 'registered' atd.)
    
    # filtr = request.args.get('color')
    # if filtr: 
    #     data = [i for i in data if i.get('color') == filtr]
    
    # -----------------------------------------------------------------
        
    return jsonify(data), 200

@app.route('/ENTITA/<int:id>', methods=['GET'])
def get_one(id):
    # Najde jeden záznam podle ID
    item = next((i for i in load_data()['ENTITA'] if i['id'] == id), None)
    return (jsonify(item), 200) if item else (jsonify({"error": "Not found"}), 404)

@app.route('/ENTITA', methods=['POST'])
def create():
    db = load_data()
    # Převezmeme data od klienta a rovnou je "vyčistíme" přes naši sanitizační funkci
    new_item = sanitize_dict(request.json) 
    
    # Vypočítáme nové ID (najdeme nejvyšší existující a přidáme 1)
    new_item['id'] = max((i['id'] for i in db['ENTITA']), default=0) + 1
    
    # Uložíme do databáze
    db['ENTITA'].append(new_item)
    save_data(db)
    return jsonify(new_item), 201


# =========================================================================
# ⚠️ TADY POZOR: PONECH POUZE TU METODU, KTEROU ZADÁNÍ VYŽADUJE! ⚠️
# POKUD CHTĚJÍ ÚPRAVU, NECH PATCH. POKUD CHTĚJÍ MAZÁNÍ, NECH DELETE.
# =========================================================================

# ---> VARIANTA: ÚPRAVA ZÁZNAMU (Metoda PATCH) <---
@app.route('/ENTITA/<int:id>', methods=['PATCH', 'PUT']) 
def update(id):
    db = load_data()
    # Najdeme záznam
    item = next((i for i in db['ENTITA'] if i['id'] == id), None)
    if not item: return jsonify({"error": "Not found"}), 404
    
    # Sloučíme stará data s novými, která jsme nejprve vyčistili (sanitizace)
    item.update(sanitize_dict(request.json))
    save_data(db)
    return jsonify(item), 200

# ---> VARIANTA: SMAZÁNÍ ZÁZNAMU (Metoda DELETE) <---
# @app.route('/ENTITA/<int:id>', methods=['DELETE']) 
# def delete(id):
#     db = load_data()
#     item = next((i for i in db['ENTITA'] if i['id'] == id), None)
#     if not item: return jsonify({"error": "Not found"}), 404
#     
#     # Odstraníme z databáze a vrátíme správný prázdný kód 204
#     db['ENTITA'].remove(item)
#     save_data(db)
#     return '', 204

if __name__ == '__main__':
    app.run(port=8001)