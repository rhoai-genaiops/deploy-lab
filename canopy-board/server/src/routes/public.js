const express = require('express');
const router = express.Router();
const { getUserLeaderboard, getTeamLeaderboard } = require('../utils/leaderboard');
const { getUserHistory, getTeamHistory } = require('../controllers/transactionsController');
const { getAllAchievements, getUserAchievementsById, getTeamAchievementsById } = require('../controllers/achievementsController');
const { getAllTeams, getTeamById } = require('../controllers/teamsController');
const { getUserById } = require('../controllers/usersController');

// Leaderboards
router.get('/leaderboard/users', (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50;
    const offset = parseInt(req.query.offset) || 0;
    const result = getUserLeaderboard(limit, offset);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/leaderboard/teams', (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50;
    const offset = parseInt(req.query.offset) || 0;
    const result = getTeamLeaderboard(limit, offset);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Historical stats
router.get('/stats/user/:userId/history', getUserHistory);
router.get('/stats/team/:teamId/history', getTeamHistory);

// Achievements
router.get('/achievements', getAllAchievements);
router.get('/achievements/user/:userId', getUserAchievementsById);
router.get('/achievements/team/:teamId', getTeamAchievementsById);

// Teams (read-only)
router.get('/teams', getAllTeams);
router.get('/teams/:id', getTeamById);

// Users (read-only)
router.get('/users/:id', getUserById);

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

module.exports = router;
