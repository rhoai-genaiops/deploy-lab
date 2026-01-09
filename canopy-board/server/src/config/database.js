const DatabaseSchema = require('../models/schema');
const path = require('path');
const fs = require('fs');

const dbDir = path.join(__dirname, '../../db');
const dbPath = process.env.DB_PATH || path.join(dbDir, 'canopy-credits.db');

// Ensure database directory exists
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

// Initialize database
const dbSchema = new DatabaseSchema(dbPath);
dbSchema.initialize();

module.exports = dbSchema.getDatabase();
