const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

const DB_FILE = 'db.json';

const loadData = () => JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
const saveData = (data) => fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));

// Sanitizace vstupu pro JS [cite: 213, 280]
const sanitize = (obj) => {
    let clean = {};
    for (let key in obj) {
        clean[key] = typeof obj[key] === 'string' ? obj[key].replace(/</g, "&lt;").replace(/>/g, "&gt;") : obj[key];
    }
    return clean;
};

app.use((req, res, next) => {
    res.setHeader('X-Server-ID', '2'); // Povinná hlavička [cite: 138, 205]
    next();
});

app.get('/items', (req, res) => {
    let data = loadData().items;
    
    // UNIVERZÁLNÍ FILTR (Dynamicky kontroluje query parametry)
    for (let key in req.query) {
        data = data.filter(i => String(i[key]) === String(req.query[key]));
    }
    
    res.status(200).json(data);
});

app.get('/items/:id', (req, res) => {
    const item = loadData().items.find(i => i.id === parseInt(req.params.id));
    item ? res.status(200).json(item) : res.status(404).json({ error: 'Not found' });
});

app.post('/items', (req, res) => {
    const db = loadData();
    const cleanBody = sanitize(req.body); // Vyčistíme vstup! [cite: 213, 280]
    const newItem = { ...cleanBody, id: db.items.length ? Math.max(...db.items.map(i => i.id)) + 1 : 1 }; // Ignoruje ID [cite: 139, 206]
    db.items.push(newItem);
    saveData(db);
    res.status(201).json(newItem);
});

// --- ÚPRAVA ZÁZNAMU (PATCH) [cite: 188, 256] ---
app.patch('/items/:id', (req, res) => { 
    const db = loadData();
    const index = db.items.findIndex(i => i.id === parseInt(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    
    db.items[index] = { ...db.items[index], ...sanitize(req.body) };
    saveData(db);
    res.status(200).json(db.items[index]);
});

// --- SMAZÁNÍ ZÁZNAMU (DELETE) [cite: 115, 140] ---
app.delete('/items/:id', (req, res) => {
    const db = loadData();
    const index = db.items.findIndex(i => i.id === parseInt(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });
    
    db.items.splice(index, 1);
    saveData(db);
    res.status(204).send(); // Vrací 204 No Content [cite: 140]
});

app.listen(8002, () => console.log('JS Server 8002'));