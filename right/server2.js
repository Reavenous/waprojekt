const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

const DB_FILE = 'db.json';

function loadData() {
    return JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
}

function saveData(data) {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
}

// Middleware pro přidání hlavičky X-Server-ID: 2
app.use((req, res, next) => {
    res.setHeader('X-Server-ID', '2');
    next();
});

app.get('/protocols', (req, res) => {
    let protocols = loadData().protocols;
    
    // Filtrování podle statusu z URL parametrů
    if (req.query.status) {
        protocols = protocols.filter(p => p.status === req.query.status);
    }
    
    res.status(200).json(protocols);
});

app.get('/protocols/:id', (req, res) => {
    const protocol = loadData().protocols.find(p => p.id === parseInt(req.params.id));
    protocol ? res.status(200).json(protocol) : res.status(404).json({ error: 'Not found' });
});

app.post('/protocols', (req, res) => {
    const data = loadData();
    // Vytvoření nového ID a ignorování případného ID z requestu
    const newId = data.protocols.length > 0 ? Math.max(...data.protocols.map(p => p.id)) + 1 : 1;
    
    const newProtocol = { ...req.body, id: newId };
    data.protocols.push(newProtocol);
    saveData(data);
    
    res.status(201).json(newProtocol);
});

app.delete('/protocols/:id', (req, res) => {
    const data = loadData();
    const index = data.protocols.findIndex(p => p.id === parseInt(req.params.id));
    
    if (index === -1) {
        return res.status(404).json({ error: 'Not found' });
    }
    
    data.protocols.splice(index, 1);
    saveData(data);
    res.status(204).send(); // 204 No Content při úspěchu
});

app.listen(8002, () => console.log('Server 2 (JS) bezi na portu 8002'));