const express = require("express");
const fs = require("fs");
const app = express();
app.use(express.json());

//  HELPERS 
function loadData() { return JSON.parse(fs.readFileSync("db.json","utf-8")); }
function saveData(data) { fs.writeFileSync("db.json", JSON.stringify(data,null,2)); }

const sanitize = (obj) => {
    let clean = {};
    for (let key in obj) {
        clean[key] = typeof obj[key] === 'string' ? obj[key].replace(/</g, "&lt;").replace(/>/g, "&gt;") : obj[key];
    }
    return clean;
};

//  GET ALL 
app.get("/books", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    let records = data.books;   // 🟡 ZDE ZMĚŇ
    
    // 🔵 FILTR (smazat tyto 2 řádky, pokud zadání filtr nechce)
    const sf = req.query.genre; // 🟡 ZDE ZMĚŇ "status"
    if (sf) records = records.filter(r => String(r.genre) === String(sf)); // 🟡 ZDE ZMĚŇ "r.status"
    
    res.set("X-Server-ID", "2");
    res.status(200).json(records);   
});

//  GET ONE 
app.get("/books/:id", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const id = parseInt(req.params.id);
    const record = data.books.find(r => r.id === id);   // 🟡 ZDE ZMĚŇ
    res.set("X-Server-ID", "2");
    if (!record) return res.status(404).json({ error: "Not found" });
    res.status(200).json(record);
});

//  POST CREATE 
app.post("/books", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const newRecord = sanitize(req.body);
    const maxId = data.books.reduce((max,r) => Math.max(max,r.id), 0);   // 🟡 ZDE ZMĚŇ
    newRecord.id = maxId + 1;
    data.books.push(newRecord);   // 🟡 ZDE ZMĚŇ
    saveData(data);
    res.set("X-Server-ID", "2");
    res.status(201).json(newRecord);
});



//  DELETE (🔵 Použij pouze pro smazání záznamu) 
app.delete("/books/:id", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const id = parseInt(req.params.id);
    const index = data.books.findIndex(r => r.id === id); // 🟡 ZDE ZMĚŇ
    res.set("X-Server-ID", "2");
    if (index === -1) return res.status(404).json({ error: "Not found" });
    
    data.books.splice(index, 1); // 🟡 ZDE ZMĚŇ
    saveData(data);
    res.status(204).send();
});

app.listen(8002, () => console.log("Server 2 running on port 8002"));