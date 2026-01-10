const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Middleware to parse JSON
app.use(express.json());

// Serve static frontend
app.use(express.static(path.join(__dirname, '../client')));

// Sample API endpoint for nonprofits
app.get('/api/nonprofits', (req, res) => {
    // Example data — later replace with PostgreSQL query
    const nonprofits = [
        { EIN: '366018535', Organization: 'GENERAL SERVICE FOUNDATION', TotalRevenue: 7548690, GrantsPaid: 3321000, AdminExpense: 193718 }
    ];
    res.json(nonprofits);
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
