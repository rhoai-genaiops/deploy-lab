const express = require('express');
const router = express.Router();
const { createTeam, updateTeam, deleteTeam } = require('../controllers/teamsController');
const { createUser, updateUser, deleteUser, getAllUsers } = require('../controllers/usersController');
const { awardCoins, awardTeamCoins, bulkAwardCoins } = require('../controllers/transactionsController');
const { createAchievement, updateAchievement, deleteAchievement } = require('../controllers/achievementsController');
const db = require('../config/database');

// Team management (auth required via middleware in index.js)
router.post('/teams', createTeam);
router.put('/teams/:id', updateTeam);
router.delete('/teams/:id', deleteTeam);

// User management
router.get('/users', getAllUsers);
router.post('/users', createUser);
router.put('/users/:id', updateUser);
router.delete('/users/:id', deleteUser);

// Coin awarding
router.post('/transactions', awardCoins);
router.post('/transactions/team', awardTeamCoins);
router.post('/transactions/bulk', bulkAwardCoins);

// Achievement management
router.post('/achievements', createAchievement);
router.put('/achievements/:id', updateAchievement);
router.delete('/achievements/:id', deleteAchievement);

// Admin statistics
router.get('/stats', (req, res) => {
  try {
    const totalUsers = db.prepare('SELECT COUNT(*) as count FROM users').get().count;
    const totalTeams = db.prepare('SELECT COUNT(*) as count FROM teams').get().count;
    const totalCoins = db.prepare('SELECT COALESCE(SUM(amount), 0) as total FROM transactions').get().total;

    const recentTransactions = db.prepare(`
      SELECT t.*, u.name as user_name, tm.name as team_name
      FROM transactions t
      LEFT JOIN users u ON t.user_id = u.id
      JOIN teams tm ON t.team_id = tm.id
      ORDER BY t.created_at DESC
      LIMIT 10
    `).all();

    res.json({
      total_users: totalUsers,
      total_teams: totalTeams,
      total_coins_awarded: totalCoins,
      recent_transactions: recentTransactions
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
