const db = require('../config/database');

/**
 * Calculate rank change compared to previous period
 */
function calculateRankChange(currentRank, previousRank) {
  if (!previousRank) return 0;
  return previousRank - currentRank; // Positive means moved up
}

/**
 * Get user leaderboard with rankings
 */
function getUserLeaderboard(limit = 50, offset = 0) {
  const users = db.prepare(`
    SELECT
      ROW_NUMBER() OVER (ORDER BY total_coins DESC, id ASC) as rank,
      *
    FROM user_leaderboard
    ORDER BY total_coins DESC, id ASC
    LIMIT ? OFFSET ?
  `).all(limit, offset);

  const total = db.prepare('SELECT COUNT(*) as count FROM users').get().count;

  return {
    users,
    total,
    page: Math.floor(offset / limit) + 1,
    pages: Math.ceil(total / limit)
  };
}

/**
 * Get team leaderboard with rankings
 */
function getTeamLeaderboard(limit = 50, offset = 0) {
  const teams = db.prepare(`
    SELECT
      ROW_NUMBER() OVER (ORDER BY total_coins DESC, id ASC) as rank,
      *
    FROM team_leaderboard
    ORDER BY total_coins DESC, id ASC
    LIMIT ? OFFSET ?
  `).all(limit, offset);

  const total = db.prepare('SELECT COUNT(*) as count FROM teams').get().count;

  return {
    teams,
    total,
    page: Math.floor(offset / limit) + 1,
    pages: Math.ceil(total / limit)
  };
}

module.exports = {
  getUserLeaderboard,
  getTeamLeaderboard,
  calculateRankChange
};
