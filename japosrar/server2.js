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

app.use((req, res, next) => {
    res.setHeader('X-Server-ID', '2');
    next();
});

app.get('/socks', (req, res) => {
    let socks = loadData().socks;
    
    // Filtrování podle barvy
    if (req.query.color) {
        socks = socks.filter(p => p.color === req.query.color);
    }
    
    res.status(200).json(socks);
});

app.get('/socks/:id', (req, res) => {
    const sock = loadData().socks.find(p => p.id === parseInt(req.params.id));
    sock ? res.status(200).json(sock) : res.status(404).json({ error: 'Not found' });
});

app.post('/socks', (req, res) => {
    const data = loadData();
    const newId = data.socks.length > 0 ? Math.max(...data.socks.map(p => p.id)) + 1 : 1;
    
    const newSock = { ...req.body, id: newId };
    data.socks.push(newSock);
    saveData(data);
    
    res.status(201).json(newSock);
});

// ÚPRAVA ZÁZNAMU MÍSTO MAZÁNÍ
app.patch('/socks/:id', (req, res) => {
    const data = loadData();
    const index = data.socks.findIndex(p => p.id === parseInt(req.params.id));
    
    if (index === -1) {
        return res.status(404).json({ error: 'Not found' });
    }
    
    // Zkopíruje stará data a přepíše je novými z požadavku (např. { found: true })
    data.socks[index] = { ...data.socks[index], ...req.body };
    saveData(data);
    
    res.status(200).json(data.socks[index]);
});

app.listen(8002, () => console.log('Server 2 (JS) bezi na portu 8002'));