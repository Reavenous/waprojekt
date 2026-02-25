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

app.get('/animals', (req, res) => {
    const data = loadData();
    res.set('X-Server-ID', '2');
    res.json(data.animals);
});

app.get('/animals/:id', (req, res) => {
    const data = loadData();
    const animal = data.animals.find(a => a.id === Number(req.params.id));

    if (!animal) {
        return res.status(404).json({ error: 'Not found' });
    }

    res.set('X-Server-ID', '2');
    res.json(animal);
});

app.post('/animals', (req, res) => {
    const data = loadData();
    const body = req.body || {};

    const newId = data.animals.length
        ? Math.max(...data.animals.map(a => a.id)) + 1
        : 1;

    const animal = {
        id: newId,
        species: String(body.species || '').trim(),
        breed: String(body.breed || '').trim(),
        birthDate: body.birthDate || '',
        registered: Boolean(body.registered)
    };

    data.animals.push(animal);
    saveData(data);

    res.status(201);
    res.set('X-Server-ID', '2');
    res.json(animal);
});

app.put('/animals/:id', (req, res) => {
    const data = loadData();
    const animal = data.animals.find(a => a.id === Number(req.params.id));

    if (!animal) {
        return res.status(404).json({ error: 'Not found' });
    }

    Object.assign(animal, req.body);
    saveData(data);

    res.set('X-Server-ID', '2');
    res.json(animal);
});

app.listen(8002, () => {
    console.log('Server 2 běží na portu 8002');
});