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
app.get("/protocols", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    let records = data.protocols;   // 🟡 ZDE ZMĚŇ
    
    // 🔵 FILTR (smazat tyto 2 řádky, pokud zadání filtr nechce)
    const sf = req.query.status; // 🟡 ZDE ZMĚŇ "status"
    if (sf) records = records.filter(r => String(r.status) === String(sf)); // 🟡 ZDE ZMĚŇ "r.status"
    
    res.set("X-Server-ID", "2");
    res.status(200).json(records);   
});

//  GET ONE 
app.get("/protocols/:id", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const id = parseInt(req.params.id);
    const record = data.protocols.find(r => r.id === id);   // 🟡 ZDE ZMĚŇ
    res.set("X-Server-ID", "2");
    if (!record) return res.status(404).json({ error: "Not found" });
    res.status(200).json(record);
});

//  POST CREATE 
app.post("/protocols", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const newRecord = sanitize(req.body);
    const maxId = data.protocols.reduce((max,r) => Math.max(max,r.id), 0);   // 🟡 ZDE ZMĚŇ
    newRecord.id = maxId + 1;
    data.protocols.push(newRecord);   // 🟡 ZDE ZMĚŇ
    saveData(data);
    res.set("X-Server-ID", "2");
    res.status(201).json(newRecord);
});

//  PUT / PATCH UPDATE (🔵 Použij pouze pro úpravu záznamu) 
app.patch("/protocols/:id", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const id = parseInt(req.params.id);
    const index = data.protocols.findIndex(r => r.id === id); // 🟡 ZDE ZMĚŇ
    res.set("X-Server-ID", "2");
    if (index === -1) return res.status(404).json({ error: "Not found" });
    
    const updates = sanitize(req.body);
    delete updates.id;
    data.protocols[index] = { ...data.protocols[index], ...updates }; // 🟡 ZDE ZMĚŇ
    saveData(data);
    res.status(200).json(data.protocols[index]); // 🟡 ZDE ZMĚŇ
});

//  DELETE (🔵 Použij pouze pro smazání záznamu) 
app.delete("/protocols/:id", (req, res) => {   // 🟡 ZDE ZMĚŇ
    const data = loadData();
    const id = parseInt(req.params.id);
    const index = data.protocols.findIndex(r => r.id === id); // 🟡 ZDE ZMĚŇ
    res.set("X-Server-ID", "2");
    if (index === -1) return res.status(404).json({ error: "Not found" });
    
    data.protocols.splice(index, 1); // 🟡 ZDE ZMĚŇ
    saveData(data);
    res.status(204).send();
});

app.listen(8002, () => console.log("Server 2 running on port 8002"));