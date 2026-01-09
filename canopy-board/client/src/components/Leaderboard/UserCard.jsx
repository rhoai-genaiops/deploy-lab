import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Award, TrendingUp } from 'lucide-react';
import TrendModal from '../Charts/TrendModal';

export default function UserCard({ user, rank }) {
  const [showTrendModal, setShowTrendModal] = useState(false);

  const getRankIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/30';
    if (rank === 2) return 'text-gray-400 bg-gray-50 dark:bg-gray-700';
    if (rank === 3) return 'text-orange-600 bg-orange-50 dark:bg-orange-900/30';
    return 'text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700';
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <>
      <motion.div
        whileHover={{ scale: 1.02, y: -2 }}
        className={`card flex items-center justify-between ${
          rank <= 3 ? 'ring-2 ring-offset-2' : ''
        } ${rank === 1 ? 'ring-yellow-400' : rank === 2 ? 'ring-gray-300' : rank === 3 ? 'ring-orange-400' : ''}`}
      >
      {/* Left side: Rank and User Info */}
      <div className="flex items-center space-x-4">
        {/* Rank Badge */}
        <div
          className={`w-14 h-14 rounded-full flex items-center justify-center text-xl font-bold ${getRankColor(
            rank
          )}`}
        >
          {getRankIcon(rank)}
        </div>

        {/* Avatar */}
        <div
          className="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-lg"
          style={{ backgroundColor: user.team_color || '#3B82F6' }}
        >
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            getInitials(user.name)
          )}
        </div>

        {/* User Info */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">{user.name}</h3>
          <div className="flex items-center space-x-2">
            <span
              className="text-sm px-2 py-0.5 rounded-full"
              style={{
                backgroundColor: user.team_color + '20',
                color: user.team_color || '#3B82F6',
              }}
            >
              {user.team_name}
            </span>
            {user.achievement_count > 0 && (
              <span className="flex items-center space-x-1 text-xs text-gray-600 dark:text-gray-400">
                <Award size={12} />
                <span>{user.achievement_count}</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right side: Coins and Trend Button */}
      <div className="flex items-center space-x-4">
        <div className="text-right">
          <div className="flex items-center space-x-2">
            <img
              src="/assets/llama-coin.png"
              alt="coin"
              className="w-7 h-7 animate-wiggle"
            />
            <motion.span
              key={user.total_coins}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              className="text-2xl font-bold text-llama-gold"
            >
              {user.total_coins.toLocaleString()}
            </motion.span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">llama-coins</p>
        </div>

        {/* Trend Button */}
        <button
          onClick={() => setShowTrendModal(true)}
          className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
          aria-label="View trends"
        >
          <TrendingUp size={20} />
        </button>
      </div>
    </motion.div>

      <TrendModal
        isOpen={showTrendModal}
        onClose={() => setShowTrendModal(false)}
        entity={user}
        type="user"
      />
    </>
  );
}
