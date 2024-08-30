const express = require("express");
const fs = require("fs");
const path = require("path");
const app = express();
const port = 1964;

app.use(express.static(path.join(__dirname, 'web')));
app.use(express.json());

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'web', 'index.html'))
})

app.post('/command', (req, res) => {
    console.log(req.body.content);

    fetch('http://localhost:5000/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: req.body.content})
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        res.json(data);
    })
    .catch(error => console.error('Error:', error));
})

app.get('/get-constants', (req, res) => {
    fetch('http://localhost:5000/get-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user: {id: 'admin', pw: 'admin'}, name: 'constants' })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        res.json(data);
    })
    .catch(error => {
        console.error('Error:', error);
        res.json({status: 404});
    });
});

app.get('/get-tokens', (req, res) => {
    fetch('http://localhost:5000/get-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user: {id: 'admin', pw: 'admin'}, name: 'tokens' })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        res.json(data);
    })
    .catch(error => {
        console.error('Error:', error);
        res.json({status: 404});
    });
});

app.get('/get-prompt', (req, res) => {
    fetch('http://localhost:5000/get-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user: {id: 'admin', pw: 'admin'}, name: 'prompt' })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        res.json(data);
    })
    .catch(error => {
        console.error('Error:', error);
        res.json({status: 404});
    });
});

app.get('/save-constants', (req, res) => {

});

app.get('/save-tokens', (req, res) => {

});

app.get('/save-prompt', (req, res) => {

});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
})