/**
 * Server 2 - Express.js Server pro správu nápojového lístku
 * Port: 8002
 */

const express = require('express');
const fs = require('fs');
const app = express();

app.use(express.json());
app.set('json spaces', 2);

const DB_FILE = 'db.json';

function loadData() {
    try {
        return JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
    } catch {
        return { drinks: [] };
    }
}

function saveData(data) {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf-8');
}

app.get('/drinks', (request, response) => {
    const data = loadData();
    response.json({ drinks: data.drinks, server: 2 });
});

app.get('/drinks/:id', (request, response) => {
    const data = loadData();
    const id = parseInt(request.params.id);
    const drink = data.drinks.find(d => d.id === id);

    if (!drink) {
        return response.status(404).json({ error: 'Drink not found', server: 2 });
    }
    response.json({ ...drink, server: 2 });
});

app.post('/drinks', (request, response) => {
    const data = loadData();
    const newDrink = request.body;

    if (!newDrink.name) {
        return response.status(400).json({ error: 'Drink name missing', server: 2 });
    }

    const maxId = data.drinks.length > 0 ? Math.max(...data.drinks.map(drink => drink.id)) : 0;
    newDrink.id = maxId + 1;

    if (newDrink.available === undefined) newDrink.available = true;

    data.drinks.push(newDrink);
    saveData(data);
    response.status(201).json({ ...newDrink, server: 2 });
});

app.put('/drinks/:id', (request, response) => {
    const data = loadData();
    const id = parseInt(request.params.id);
    const index = data.drinks.findIndex(drink => drink.id === id);

    if (index === -1) {
        return response.status(404).json({ error: 'Drink not found', server: 2 });
    }

    const updatedData = request.body;

    const originalId = data.drinks[index].id;
    data.drinks[index] = { ...data.drinks[index], ...updatedData, id: originalId };

    saveData(data);
    response.json({ ...data.drinks[index], server: 2 });
});

app.listen(8002, () => {
    console.log('Server 2 (JS) runs on port 8002');
});