const express = require("express");
const fs = require("fs");
const app = express();
app.use(express.json());

//  HELPERS  (never change)
function loadData() { return JSON.parse(fs.readFileSync("db.json","utf-8")); }
function saveData(data) { fs.writeFileSync("db.json", JSON.stringify(data,null,2)); }

//  GET ALL
app.get("/games", (req, res) => {   
    const data = loadData();
    let records = data.games;   
    // --- filter block: delete these 2 lines if exam has no filter ---
    const sf = req.query.status;
    if (sf) records = records.filter(r => r.status === sf);
    // ------------------------------------------------------------------
    res.set("X-Server-ID", "2");
    res.status(200).json({ games: records, server: 2 });   
});

//  GET ONE
app.get("/games/:id", (req, res) => {   
    const data = loadData();
    // IMPORTANT: req.params.id is always a STRING – must parseInt!
    const id = parseInt(req.params.id);
    const record = data.games.find(r => r.id === id);   
    res.set("X-Server-ID", "2");
    if (!record) return res.status(404).json({ error: "Not found" });
    res.status(200).json(record);
});

//  POST CREATE
app.post("/games", (req, res) => {  
    const data = loadData();
    const newRecord = req.body;
    const maxId = data.games.reduce((max,r) => Math.max(max,r.id), 0);   
    newRecord.id = maxId + 1;
    data.games.push(newRecord);  
    saveData(data);
    res.set("X-Server-ID", "2");
    res.status(201).json({ ...newRecord, server: 2 });
});

//  PUT UPDATE  (only if exam asks for update)
app.put("/games/:id", (req, res) => {   // change "protocols"
    const data = loadData();
    const id = parseInt(req.params.id);
    const index = data.games.findIndex(r => r.id === id);
    res.set("X-Server-ID", "2");
    if (index === -1) return res.status(404).json({ error: "Not found" });
    const updates = req.body;
    delete updates.id;   // never overwrite the id!
    data.games[index] = { ...data.games[index], ...updates };
    saveData(data);
    res.status(200).json({ ...data.games[index], server: 2 });
});



//  START  (never change)
app.listen(8002, () => console.log("Server 2 running on port 8002"));