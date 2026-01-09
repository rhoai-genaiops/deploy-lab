const db = require('../config/database');
const { checkUserAchievements, checkTeamAchievements } = require('../utils/achievements');

/**
 * Award coins to a user (admin only)
 */
function awardCoins(req, res) {
  try {
    const { user_id, amount, reason } = req.body;

    if (!user_id || !amount || !reason) {
      return res.status(400).json({
        error: 'user_id, amount, and reason are required'
      });
    }

    // Verify user exists and get their team
    const user = db.prepare('SELECT id, team_id FROM users WHERE id = ?').get(user_id);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Insert transaction
    const insert = db.prepare(`
      INSERT INTO transactions (user_id, team_id, amount, reason, awarded_by)
      VALUES (?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      user_id,
      user.team_id,
      amount,
      reason,
      'admin' // Could be enhanced to track which admin
    );

    // Check for new achievements
    const userAchievements = checkUserAchievements(user_id);
    const teamAchievements = checkTeamAchievements(user.team_id);

    const transaction = db.prepare('SELECT * FROM transactions WHERE id = ?').get(result.lastInsertRowid);

    res.status(201).json({
      transaction,
      new_achievements: {
        user: userAchievements,
        team: teamAchievements
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Award coins to multiple users (bulk operation)
 */
function bulkAwardCoins(req, res) {
  try {
    const { awards } = req.body;

    if (!Array.isArray(awards) || awards.length === 0) {
      return res.status(400).json({ error: 'awards array is required' });
    }

    const transactions = [];
    const newAchievements = [];

    const insert = db.prepare(`
      INSERT INTO transactions (user_id, team_id, amount, reason, awarded_by)
      VALUES (?, ?, ?, ?, ?)
    `);

    const bulkInsert = db.transaction((awards) => {
      for (const award of awards) {
        const { user_id, amount, reason } = award;

        if (!user_id || !amount || !reason) {
          throw new Error('Each award must have user_id, amount, and reason');
        }

        const user = db.prepare('SELECT id, team_id FROM users WHERE id = ?').get(user_id);
        if (!user) {
          throw new Error(`User ${user_id} not found`);
        }

        const result = insert.run(user_id, user.team_id, amount, reason, 'admin');
        const transaction = db.prepare('SELECT * FROM transactions WHERE id = ?').get(result.lastInsertRowid);
        transactions.push(transaction);

        // Check achievements
        const userAch = checkUserAchievements(user_id);
        const teamAch = checkTeamAchievements(user.team_id);

        if (userAch.length > 0 || teamAch.length > 0) {
          newAchievements.push({
            user_id,
            user: userAch,
            team: teamAch
          });
        }
      }
    });

    bulkInsert(awards);

    res.status(201).json({ transactions, new_achievements: newAchievements });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Award coins directly to a team (admin only)
 */
function awardTeamCoins(req, res) {
  try {
    const { team_id, amount, reason } = req.body;

    if (!team_id || !amount || !reason) {
      return res.status(400).json({
        error: 'team_id, amount, and reason are required'
      });
    }

    // Verify team exists
    const team = db.prepare('SELECT id, name FROM teams WHERE id = ?').get(team_id);
    if (!team) {
      return res.status(404).json({ error: 'Team not found' });
    }

    // Insert transaction with NULL user_id (team-only award)
    const insert = db.prepare(`
      INSERT INTO transactions (user_id, team_id, amount, reason, awarded_by)
      VALUES (?, ?, ?, ?, ?)
    `);

    const result = insert.run(
      null,  // user_id is NULL for team awards
      team_id,
      amount,
      reason,
      'admin'
    );

    // Check for new team achievements
    const teamAchievements = checkTeamAchievements(team_id);

    const transaction = db.prepare('SELECT * FROM transactions WHERE id = ?').get(result.lastInsertRowid);

    res.status(201).json({
      transaction,
      new_achievements: {
        team: teamAchievements
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get coin history for a user
 */
function getUserHistory(req, res) {
  try {
    const { userId } = req.params;
    const { period = '30d' } = req.query;

    // Calculate date range based on period
    const periodMap = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '1y': 365,
      'all': null
    };

    const days = periodMap[period];
    let dateFilter = '';
    if (days) {
      dateFilter = `AND created_at >= datetime('now', '-${days} days')`;
    }

    // Get transactions
    const transactions = db.prepare(`
      SELECT
        date(created_at) as date,
        SUM(amount) as daily_coins
      FROM transactions
      WHERE user_id = ? ${dateFilter}
      GROUP BY date(created_at)
      ORDER BY date ASC
    `).all(userId);

    // Calculate cumulative totals
    let cumulative = 0;
    const data = transactions.map(t => {
      cumulative += t.daily_coins;
      return {
        date: t.date,
        daily_coins: t.daily_coins,
        cumulative_coins: cumulative
      };
    });

    res.json({ user_id: parseInt(userId), period, data });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get coin history for a team
 */
function getTeamHistory(req, res) {
  try {
    const { teamId } = req.params;
    const { period = '30d' } = req.query;

    const periodMap = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '1y': 365,
      'all': null
    };

    const days = periodMap[period];
    let dateFilter = '';
    if (days) {
      dateFilter = `AND created_at >= datetime('now', '-${days} days')`;
    }

    const transactions = db.prepare(`
      SELECT
        date(created_at) as date,
        SUM(amount) as daily_coins
      FROM transactions
      WHERE team_id = ? ${dateFilter}
      GROUP BY date(created_at)
      ORDER BY date ASC
    `).all(teamId);

    let cumulative = 0;
    const data = transactions.map(t => {
      cumulative += t.daily_coins;
      return {
        date: t.date,
        daily_coins: t.daily_coins,
        cumulative_coins: cumulative
      };
    });

    res.json({ team_id: parseInt(teamId), period, data });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  awardCoins,
  awardTeamCoins,
  bulkAwardCoins,
  getUserHistory,
  getTeamHistory
};
