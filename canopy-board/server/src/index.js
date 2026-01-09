require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');

const publicRoutes = require('./routes/public');
const adminRoutes = require('./routes/admin');
const { verifyAdminToken } = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// Middleware
app.use(helmet({
  contentSecurityPolicy: false, // Allow inline scripts for React
}));

app.use(cors({
  origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : '*',
  credentials: true
}));

app.use(compression());
app.use(morgan(NODE_ENV === 'production' ? 'combined' : 'dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API Routes
app.use('/api', publicRoutes);

// Admin auth routes (login/verify - no auth required)
const adminAuthRoutes = require('./routes/adminAuth');
app.use('/api/admin', adminAuthRoutes);

// Protected admin routes (auth required)
app.use('/api/admin', verifyAdminToken, adminRoutes);

// Serve static files from React build (in production)
const staticPath = path.join(__dirname, '../public');
app.use(express.static(staticPath));

// Serve React app for all other routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(staticPath, 'index.html'), (err) => {
    if (err) {
      res.status(500).json({
        error: 'Frontend not built. Run: cd client && npm run build'
      });
    }
  });
});

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🦙  CANOPY CREDITS BOARD  🦙                          ║
║                                                            ║
║     Server running on: http://localhost:${PORT}            ║
║     Environment: ${NODE_ENV.padEnd(37)}║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
  `);

  if (NODE_ENV === 'development') {
    console.log('\nAPI Endpoints:');
    console.log('  Public API:  http://localhost:${PORT}/api');
    console.log('  Admin API:   http://localhost:${PORT}/api/admin');
    console.log('  Health:      http://localhost:${PORT}/api/health\n');
  }
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, closing server...');
  process.exit(0);
});
