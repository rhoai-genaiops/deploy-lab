const db = require('../config/database');

/**
 * Get all teams
 */
function getAllTeams(req, res) {
  try {
    const teams = db.prepare('SELECT * FROM teams ORDER BY name ASC').all();
    res.json({ teams });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get a single team by ID
 */
function getTeamById(req, res) {
  try {
    const { id } = req.params;
    const team = db.prepare('SELECT * FROM teams WHERE id = ?').get(id);

    if (!team) {
      return res.status(404).json({ error: 'Team not found' });
    }

    // Get team members
    const members = db.prepare('SELECT * FROM users WHERE team_id = ? ORDER BY name ASC').all(id);

    res.json({ team, members });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Create a new team (admin only)
 */
function createTeam(req, res) {
  try {
    const { name, description, color } = req.body;

    if (!name) {
      return res.status(400).json({ error: 'Team name is required' });
    }

    const insert = db.prepare(`
      INSERT INTO teams (name, description, color)
      VALUES (?, ?, ?)
    `);

    const result = insert.run(name, description || null, color || '#3B82F6');
    const team = db.prepare('SELECT * FROM teams WHERE id = ?').get(result.lastInsertRowid);

    res.status(201).json({ team });
  } catch (error) {
    if (error.message.includes('UNIQUE constraint failed')) {
      return res.status(400).json({ error: 'Team name already exists' });
    }
    res.status(500).json({ error: error.message });
  }
}

/**
 * Update a team (admin only)
 */
function updateTeam(req, res) {
  try {
    const { id } = req.params;
    const { name, description, color } = req.body;

    const update = db.prepare(`
      UPDATE teams
      SET name = COALESCE(?, name),
          description = COALESCE(?, description),
          color = COALESCE(?, color),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    const result = update.run(name, description, color, id);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Team not found' });
    }

    const team = db.prepare('SELECT * FROM teams WHERE id = ?').get(id);
    res.json({ team });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Delete a team (admin only)
 */
function deleteTeam(req, res) {
  try {
    const { id } = req.params;

    const del = db.prepare('DELETE FROM teams WHERE id = ?');
    const result = del.run(id);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Team not found' });
    }

    res.json({ success: true, message: 'Team deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  getAllTeams,
  getTeamById,
  createTeam,
  updateTeam,
  deleteTeam
};
