const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

const DB_FILE = 'db.json';

// Funkce pro načítání a ukládání souboru
const loadData = () => JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
const saveData = (data) => fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));

// --- ⚠️ SANITIZACE VSTUPU ⚠️ ---
// Vezme odeslaný JSON a pokud najde textový řetězec, nahradí nebezpečné tagy < a >
const sanitize = (obj) => {
    let clean = {};
    for (let key in obj) {
        clean[key] = typeof obj[key] === 'string' ? obj[key].replace(/</g, "&lt;").replace(/>/g, "&gt;") : obj[key];
    }
    return clean;
};

// Automaticky vloží X-Server-ID ke každé odpovědi
app.use((req, res, next) => {
    res.setHeader('X-Server-ID', '2');
    next();
});

// --- ⚠️ PŘEPIŠ 'ENTITA' VE VŠECH app.get, app.post atd. ZDE DOLE ⚠️ ---

app.get('/ENTITA', (req, res) => {
    // Načteme celou tabulku (Nezapomeň změnit .ENTITA na např. .socks)
    let data = loadData().ENTITA;
    
    // --- ⚠️ FILTROVÁNÍ (ZAPNI POUZE POKUD TO ZADÁNÍ VYŽADUJE) ⚠️ ---
    // Odstraň lomítka (//) a přepiš obě slova 'color' na název filtru ze zadání
    
    // if (req.query.color) {
    //     data = data.filter(i => i.color === req.query.color);
    // }
    
    // -----------------------------------------------------------------
    
    res.status(200).json(data);
});

app.get('/ENTITA/:id', (req, res) => {
    // Najde prvek s přesným ID
    const item = loadData().ENTITA.find(i => i.id === parseInt(req.params.id));
    item ? res.status(200).json(item) : res.status(404).json({ error: 'Not found' });
});

app.post('/ENTITA', (req, res) => {
    const db = loadData();
    // Než uložíme data, proženeme je přes naši sanitizaci
    const cleanBody = sanitize(req.body); 
    
    // Vytvoříme nové ID
    const newItem = { ...cleanBody, id: db.ENTITA.length ? Math.max(...db.ENTITA.map(i => i.id)) + 1 : 1 };
    
    db.ENTITA.push(newItem);
    saveData(db);
    res.status(201).json(newItem);
});

// =========================================================================
// ⚠️ TADY POZOR: PONECH POUZE TU METODU, KTEROU ZADÁNÍ VYŽADUJE! ⚠️
// =========================================================================

// ---> VARIANTA: ÚPRAVA ZÁZNAMU (Metoda PATCH) <---
app.patch('/ENTITA/:id', (req, res) => { 
    const db = loadData();
    const index = db.ENTITA.findIndex(i => i.id === parseInt(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    
    // Přepíše stará data novými (znovu prohnanými přes sanitizaci)
    db.ENTITA[index] = { ...db.ENTITA[index], ...sanitize(req.body) };
    saveData(db);
    res.status(200).json(db.ENTITA[index]);
});

// ---> VARIANTA: SMAZÁNÍ ZÁZNAMU (Metoda DELETE) <---
/*
app.delete('/ENTITA/:id', (req, res) => {
    const db = loadData();
    const index = db.ENTITA.findIndex(i => i.id === parseInt(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    
    // Smaže prvek z pole a vrátí kód 204
    db.ENTITA.splice(index, 1);
    saveData(db);
    res.status(204).send();
});
*/

app.listen(8002, () => console.log('JS Server běží na portu 8002'));