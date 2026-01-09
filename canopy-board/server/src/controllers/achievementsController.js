const db = require('../config/database');
const { getUserAchievements, getTeamAchievements } = require('../utils/achievements');

/**
 * Get all achievements (both user and team)
 */
function getAllAchievements(req, res) {
  try {
    const userAchievements = db.prepare(`
      SELECT * FROM achievements
      WHERE type = 'user'
      ORDER BY threshold ASC
    `).all();

    const teamAchievements = db.prepare(`
      SELECT * FROM achievements
      WHERE type = 'team'
      ORDER BY threshold ASC
    `).all();

    res.json({
      user_achievements: userAchievements,
      team_achievements: teamAchievements
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get achievements for a specific user
 */
function getUserAchievementsById(req, res) {
  try {
    const { userId } = req.params;

    // Verify user exists
    const user = db.prepare('SELECT id FROM users WHERE id = ?').get(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const achievements = getUserAchievements(userId);
    res.json(achievements);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get achievements for a specific team
 */
function getTeamAchievementsById(req, res) {
  try {
    const { teamId } = req.params;

    // Verify team exists
    const team = db.prepare('SELECT id FROM teams WHERE id = ?').get(teamId);
    if (!team) {
      return res.status(404).json({ error: 'Team not found' });
    }

    const achievements = getTeamAchievements(teamId);
    res.json(achievements);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Create a new achievement (admin only)
 */
function createAchievement(req, res) {
  try {
    const { type, name, description, icon, threshold, tier } = req.body;

    if (!type || !name || !threshold) {
      return res.status(400).json({
        error: 'type, name, and threshold are required'
      });
    }

    if (!['user', 'team'].includes(type)) {
      return res.status(400).json({ error: 'type must be "user" or "team"' });
    }

    const insert = db.prepare(`
      INSERT INTO achievements (type, name, description, icon, threshold, tier)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      type,
      name,
      description || null,
      icon || '🏆',
      threshold,
      tier || 'bronze'
    );

    const achievement = db.prepare('SELECT * FROM achievements WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json({ achievement });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Update an achievement (admin only)
 */
function updateAchievement(req, res) {
  try {
    const { id } = req.params;
    const { name, description, icon, threshold, tier } = req.body;

    const update = db.prepare(`
      UPDATE achievements
      SET name = COALESCE(?, name),
          description = COALESCE(?, description),
          icon = COALESCE(?, icon),
          threshold = COALESCE(?, threshold),
          tier = COALESCE(?, tier)
      WHERE id = ?
    `);

    const result = update.run(name, description, icon, threshold, tier, id);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Achievement not found' });
    }

    const achievement = db.prepare('SELECT * FROM achievements WHERE id = ?').get(id);
    res.json({ achievement });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Delete an achievement (admin only)
 */
function deleteAchievement(req, res) {
  try {
    const { id } = req.params;

    const del = db.prepare('DELETE FROM achievements WHERE id = ?');
    const result = del.run(id);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Achievement not found' });
    }

    res.json({ success: true, message: 'Achievement deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  getAllAchievements,
  getUserAchievementsById,
  getTeamAchievementsById,
  createAchievement,
  updateAchievement,
  deleteAchievement
};
