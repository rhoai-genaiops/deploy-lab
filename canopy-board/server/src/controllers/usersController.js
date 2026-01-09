const db = require('../config/database');

/**
 * Get all users
 */
function getAllUsers(req, res) {
  try {
    const users = db.prepare(`
      SELECT u.*, t.name as team_name, t.color as team_color
      FROM users u
      LEFT JOIN teams t ON u.team_id = t.id
      ORDER BY u.name ASC
    `).all();

    res.json({ users });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get a single user by ID
 */
function getUserById(req, res) {
  try {
    const { id } = req.params;

    const user = db.prepare(`
      SELECT u.*, t.name as team_name, t.color as team_color
      FROM users u
      LEFT JOIN teams t ON u.team_id = t.id
      WHERE u.id = ?
    `).get(id);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Get user transactions
    const transactions = db.prepare(`
      SELECT * FROM transactions
      WHERE user_id = ?
      ORDER BY created_at DESC
      LIMIT 50
    `).all(id);

    // Get total coins
    const stats = db.prepare(`
      SELECT COALESCE(SUM(amount), 0) as total_coins
      FROM transactions
      WHERE user_id = ?
    `).get(id);

    res.json({
      user,
      transactions,
      total_coins: stats.total_coins
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Create a new user (admin only)
 */
function createUser(req, res) {
  try {
    const { name, email, team_id } = req.body;

    if (!name || !team_id) {
      return res.status(400).json({ error: 'Name and team_id are required' });
    }

    // Verify team exists
    const team = db.prepare('SELECT id FROM teams WHERE id = ?').get(team_id);
    if (!team) {
      return res.status(400).json({ error: 'Team not found' });
    }

    const insert = db.prepare(`
      INSERT INTO users (name, email, team_id)
      VALUES (?, ?, ?)
    `);

    const result = insert.run(name, email || null, team_id);
    const user = db.prepare(`
      SELECT u.*, t.name as team_name, t.color as team_color
      FROM users u
      LEFT JOIN teams t ON u.team_id = t.id
      WHERE u.id = ?
    `).get(result.lastInsertRowid);

    res.status(201).json({ user });
  } catch (error) {
    if (error.message.includes('UNIQUE constraint failed')) {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: error.message });
  }
}

/**
 * Update a user (admin only)
 */
function updateUser(req, res) {
  try {
    const { id } = req.params;
    const { name, email, team_id } = req.body;

    // If team_id is provided, verify it exists
    if (team_id) {
      const team = db.prepare('SELECT id FROM teams WHERE id = ?').get(team_id);
      if (!team) {
        return res.status(400).json({ error: 'Team not found' });
      }
    }

    const update = db.prepare(`
      UPDATE users
      SET name = COALESCE(?, name),
          email = COALESCE(?, email),
          team_id = COALESCE(?, team_id),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    const result = update.run(name, email, team_id, id);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    const user = db.prepare(`
      SELECT u.*, t.name as team_name, t.color as team_color
      FROM users u
      LEFT JOIN teams t ON u.team_id = t.id
      WHERE u.id = ?
    `).get(id);

    res.json({ user });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Delete a user (admin only)
 */
function deleteUser(req, res) {
  try {
    const { id } = req.params;

    const del = db.prepare('DELETE FROM users WHERE id = ?');
    const result = del.run(id);

    if (result.changes === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ success: true, message: 'User deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  getAllUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser
};
