const express = require('express');
const app = express();
const port = 8080;

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Main app
app.get('/', (req, res) => {
  res.send('Veritas Web Service Running');
});

app.listen(port, '0.0.0.0', () => {
  console.log(`✅ Veritas web running on port ${port}`);
});
