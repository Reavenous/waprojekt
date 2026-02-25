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

app.get('/animals', (req, res) => {
    res.status(200).json(loadData().animals);
});

app.get('/animals/:id', (req, res) => {
    const animal = loadData().animals.find(a => a.id === parseInt(req.params.id));
    animal ? res.status(200).json(animal) : res.status(404).json({ error: 'Not found' });
});

app.post('/animals', (req, res) => {
    const data = loadData();
    const newAnimal = {
        ...req.body,
        id: data.animals.length > 0 ? Math.max(...data.animals.map(a => a.id)) + 1 : 1
    };
    data.animals.push(newAnimal);
    saveData(data);
    res.status(201).json(newAnimal);
});

app.patch('/animals/:id', (req, res) => {
    const data = loadData();
    const index = data.animals.findIndex(a => a.id === parseInt(req.params.id));
    if (index === -1) return res.status(404).json({ error: 'Not found' });

    data.animals[index] = { ...data.animals[index], ...req.body };
    saveData(data);
    res.status(201).json(data.animals[index]);
});

app.listen(8002, () => console.log('Server 2 běží na  http://127.0.0.1:8002'));