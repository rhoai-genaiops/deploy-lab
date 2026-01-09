const Database = require('better-sqlite3');
const path = require('path');

class DatabaseSchema {
  constructor(dbPath) {
    this.db = new Database(dbPath, { verbose: console.log });
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
  }

  initialize() {
    this.createTables();
    this.createViews();
    this.createIndexes();
    this.seedAchievements();
  }

  createTables() {
    // Teams table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        color TEXT DEFAULT '#3B82F6',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Users table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        team_id INTEGER NOT NULL,
        avatar_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
      );
    `);

    // Transactions table (coin awards/deductions)
    // user_id can be NULL for team-only awards
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        team_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        reason TEXT NOT NULL,
        awarded_by TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
      );
    `);

    // Achievements table (milestone definitions)
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        threshold INTEGER NOT NULL,
        tier TEXT DEFAULT 'bronze',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // User achievements (unlocked badges)
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
        UNIQUE(user_id, achievement_id)
      );
    `);

    // Team achievements (unlocked badges)
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS team_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
        FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
        UNIQUE(team_id, achievement_id)
      );
    `);
  }

  createIndexes() {
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_team_id ON transactions(team_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
      CREATE INDEX IF NOT EXISTS idx_users_team_id ON users(team_id);
    `);
  }

  createViews() {
    // Drop views if they exist (for updates)
    this.db.exec('DROP VIEW IF EXISTS user_leaderboard;');
    this.db.exec('DROP VIEW IF EXISTS team_leaderboard;');

    // User leaderboard view
    this.db.exec(`
      CREATE VIEW user_leaderboard AS
      SELECT
        u.id,
        u.name,
        u.email,
        u.team_id,
        t.name as team_name,
        t.color as team_color,
        COALESCE(SUM(tr.amount), 0) as total_coins,
        COALESCE((SELECT COUNT(*) FROM user_achievements WHERE user_id = u.id), 0) as achievement_count,
        MAX(tr.created_at) as last_transaction_date
      FROM users u
      LEFT JOIN teams t ON u.team_id = t.id
      LEFT JOIN transactions tr ON u.id = tr.user_id
      GROUP BY u.id, u.name, u.email, u.team_id, t.name, t.color;
    `);

    // Team leaderboard view
    this.db.exec(`
      CREATE VIEW team_leaderboard AS
      SELECT
        t.id,
        t.name,
        t.description,
        t.color,
        COALESCE((SELECT COUNT(*) FROM users WHERE team_id = t.id), 0) as member_count,
        COALESCE((SELECT SUM(amount) FROM transactions WHERE team_id = t.id), 0) as total_coins,
        COALESCE((SELECT COUNT(*) FROM team_achievements WHERE team_id = t.id), 0) as achievement_count,
        (SELECT MAX(created_at) FROM transactions WHERE team_id = t.id) as last_transaction_date
      FROM teams t;
    `);
  }

  seedAchievements() {
    // Check if achievements already exist
    const count = this.db.prepare('SELECT COUNT(*) as count FROM achievements').get();
    if (count.count > 0) {
      console.log('Achievements already seeded, skipping...');
      return;
    }

    const achievements = [
      // Bronze tier - User achievements
      { type: 'user', name: 'First Llama', description: 'Earned your first llama coin!', icon: '🦙', threshold: 1, tier: 'bronze' },
      { type: 'user', name: 'Coin Collector', description: 'Earned 10 llama coins', icon: '🪙', threshold: 10, tier: 'bronze' },
      { type: 'user', name: 'Half Century', description: 'Reached 50 llama coins', icon: '⭐', threshold: 50, tier: 'bronze' },

      // Silver tier - User achievements
      { type: 'user', name: 'Century Club', description: '100 llama coins earned!', icon: '💯', threshold: 100, tier: 'silver' },
      { type: 'user', name: 'Quarter Master', description: 'Accumulated 250 llama coins', icon: '🌟', threshold: 250, tier: 'silver' },

      // Gold tier - User achievements
      { type: 'user', name: 'Llama Legend', description: 'Reached 500 llama coins!', icon: '🏆', threshold: 500, tier: 'gold' },
      { type: 'user', name: 'Coin Titan', description: '1000 llama coins milestone', icon: '👑', threshold: 1000, tier: 'gold' },

      // Platinum tier - User achievements
      { type: 'user', name: 'Mega Llama', description: '2500 llama coins achieved!', icon: '💎', threshold: 2500, tier: 'platinum' },
      { type: 'user', name: 'Llama Emperor', description: '5000 llama coins mastery!', icon: '🔥', threshold: 5000, tier: 'platinum' },

      // Team achievements
      { type: 'team', name: 'Team Starter', description: 'Team earned first 100 coins', icon: '🎯', threshold: 100, tier: 'bronze' },
      { type: 'team', name: 'Team Player', description: 'Team reached 500 coins', icon: '🤝', threshold: 500, tier: 'silver' },
      { type: 'team', name: 'Dream Team', description: 'Team accumulated 1000 coins', icon: '🏅', threshold: 1000, tier: 'gold' },
      { type: 'team', name: 'Elite Squad', description: 'Team achieved 2500 coins', icon: '🌈', threshold: 2500, tier: 'platinum' },
      { type: 'team', name: 'Unstoppable Force', description: 'Team reached 5000 coins!', icon: '🚀', threshold: 5000, tier: 'platinum' }
    ];

    const insert = this.db.prepare(`
      INSERT INTO achievements (type, name, description, icon, threshold, tier)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const insertMany = this.db.transaction((achievements) => {
      for (const ach of achievements) {
        insert.run(ach.type, ach.name, ach.description, ach.icon, ach.threshold, ach.tier);
      }
    });

    insertMany(achievements);
    console.log(`Seeded ${achievements.length} achievements`);
  }

  getDatabase() {
    return this.db;
  }

  close() {
    this.db.close();
  }
}

module.exports = DatabaseSchema;
