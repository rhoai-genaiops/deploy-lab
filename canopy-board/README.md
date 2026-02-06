# Canopy Credits Board 🦙

A fun, interactive dashboard for tracking team efforts with CAI-coins! Go CAI!

## Configuration

### Environment Variables

- `ADMIN_PASSWORD`: Admin login password (default: "admin")
- `PORT`: Server port (default: 3000)
- `DB_PATH`: SQLite database file path (default: ./server/db/canopy-credits.db)
- `NODE_ENV`: Environment (development/production)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

## Usage

### Admin Functions

1. **Login**: Navigate to `/admin` and enter admin password
2. **Create Teams**: Add teams with names, descriptions, and colors
3. **Add Users**: Create users and assign them to teams
4. **Award Coins**: Give CAI-coins to users with reasons
5. **View Stats**: Monitor activity and recent transactions

### Public View

- View leaderboards (no login required)
- Toggle between team and individual views
- See achievements and rankings
- View historical trends

## Architecture

- **Frontend**: React 18 + Vite + Tailwind CSS + Framer Motion
- **Backend**: Node.js 20 + Express.js
- **Database**: SQLite with views for optimized queries
- **Deployment**: Docker + Kubernetes + Helm

## Database Schema

- `teams`: Team information
- `users`: User profiles
- `transactions`: Coin award/deduction history
- `achievements`: Badge definitions
- `user_achievements`: Unlocked user badges
- `team_achievements`: Unlocked team badges

## API Endpoints

### Public

- `GET /api/leaderboard/users` - User rankings
- `GET /api/leaderboard/teams` - Team rankings
- `GET /api/stats/user/:id/history` - User coin history
- `GET /api/achievements` - All achievements

### Admin (Requires Authentication)

- `POST /api/admin/login` - Get JWT token
- `POST /api/admin/teams` - Create team
- `POST /api/admin/users` - Create user
- `POST /api/admin/transactions` - Award coins

## License

MIT
