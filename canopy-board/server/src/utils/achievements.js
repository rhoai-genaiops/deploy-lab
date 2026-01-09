const db = require('../config/database');

/**
 * Check and unlock achievements for a user based on their total coins
 */
function checkUserAchievements(userId) {
  // Get user's total coins
  const userStats = db.prepare(`
    SELECT COALESCE(SUM(amount), 0) as total_coins
    FROM transactions
    WHERE user_id = ?
  `).get(userId);

  const totalCoins = userStats.total_coins;

  // Get all user achievements that could be unlocked
  const eligibleAchievements = db.prepare(`
    SELECT id, name, threshold
    FROM achievements
    WHERE type = 'user' AND threshold <= ?
    AND id NOT IN (
      SELECT achievement_id
      FROM user_achievements
      WHERE user_id = ?
    )
  `).all(totalCoins, userId);

  // Unlock new achievements
  const newAchievements = [];
  const insert = db.prepare(`
    INSERT INTO user_achievements (user_id, achievement_id)
    VALUES (?, ?)
  `);

  for (const achievement of eligibleAchievements) {
    try {
      insert.run(userId, achievement.id);
      newAchievements.push(achievement);
    } catch (error) {
      // Achievement already unlocked (race condition)
      console.error('Error unlocking achievement:', error.message);
    }
  }

  return newAchievements;
}

/**
 * Check and unlock achievements for a team based on their total coins
 */
function checkTeamAchievements(teamId) {
  // Get team's total coins
  const teamStats = db.prepare(`
    SELECT COALESCE(SUM(amount), 0) as total_coins
    FROM transactions
    WHERE team_id = ?
  `).get(teamId);

  const totalCoins = teamStats.total_coins;

  // Get all team achievements that could be unlocked
  const eligibleAchievements = db.prepare(`
    SELECT id, name, threshold
    FROM achievements
    WHERE type = 'team' AND threshold <= ?
    AND id NOT IN (
      SELECT achievement_id
      FROM team_achievements
      WHERE team_id = ?
    )
  `).all(totalCoins, teamId);

  // Unlock new achievements
  const newAchievements = [];
  const insert = db.prepare(`
    INSERT INTO team_achievements (team_id, achievement_id)
    VALUES (?, ?)
  `);

  for (const achievement of eligibleAchievements) {
    try {
      insert.run(teamId, achievement.id);
      newAchievements.push(achievement);
    } catch (error) {
      // Achievement already unlocked (race condition)
      console.error('Error unlocking team achievement:', error.message);
    }
  }

  return newAchievements;
}

/**
 * Get unlocked and locked achievements for a user
 */
function getUserAchievements(userId) {
  const totalCoins = db.prepare(`
    SELECT COALESCE(SUM(amount), 0) as total_coins
    FROM transactions
    WHERE user_id = ?
  `).get(userId).total_coins;

  const unlocked = db.prepare(`
    SELECT a.*, ua.unlocked_at
    FROM achievements a
    JOIN user_achievements ua ON a.id = ua.achievement_id
    WHERE ua.user_id = ? AND a.type = 'user'
    ORDER BY a.threshold ASC
  `).all(userId);

  const locked = db.prepare(`
    SELECT *
    FROM achievements
    WHERE type = 'user'
    AND id NOT IN (
      SELECT achievement_id
      FROM user_achievements
      WHERE user_id = ?
    )
    ORDER BY threshold ASC
  `).all(userId);

  // Find next achievement
  const nextAchievement = locked.find(a => a.threshold > totalCoins);

  return {
    unlocked,
    locked,
    progress: nextAchievement ? {
      next_achievement: nextAchievement,
      current_coins: totalCoins,
      needed_coins: nextAchievement.threshold - totalCoins
    } : null
  };
}

/**
 * Get unlocked and locked achievements for a team
 */
function getTeamAchievements(teamId) {
  const totalCoins = db.prepare(`
    SELECT COALESCE(SUM(amount), 0) as total_coins
    FROM transactions
    WHERE team_id = ?
  `).get(teamId).total_coins;

  const unlocked = db.prepare(`
    SELECT a.*, ta.unlocked_at
    FROM achievements a
    JOIN team_achievements ta ON a.id = ta.achievement_id
    WHERE ta.team_id = ? AND a.type = 'team'
    ORDER BY a.threshold ASC
  `).all(teamId);

  const locked = db.prepare(`
    SELECT *
    FROM achievements
    WHERE type = 'team'
    AND id NOT IN (
      SELECT achievement_id
      FROM team_achievements
      WHERE team_id = ?
    )
    ORDER BY threshold ASC
  `).all(teamId);

  // Find next achievement
  const nextAchievement = locked.find(a => a.threshold > totalCoins);

  return {
    unlocked,
    locked,
    progress: nextAchievement ? {
      next_achievement: nextAchievement,
      current_coins: totalCoins,
      needed_coins: nextAchievement.threshold - totalCoins
    } : null
  };
}

module.exports = {
  checkUserAchievements,
  checkTeamAchievements,
  getUserAchievements,
  getTeamAchievements
};
