import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, Award, TrendingUp } from 'lucide-react';
import TrendModal from '../Charts/TrendModal';

export default function TeamCard({ team, rank }) {
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

  return (
    <>
      <motion.div
        whileHover={{ scale: 1.02, y: -2 }}
        className={`card flex items-center justify-between ${
          rank <= 3 ? 'ring-2 ring-offset-2' : ''
        } ${rank === 1 ? 'ring-yellow-400' : rank === 2 ? 'ring-gray-300' : rank === 3 ? 'ring-orange-400' : ''}`}
      >
      {/* Left side: Rank and Team Info */}
      <div className="flex items-center space-x-4">
        {/* Rank Badge */}
        <div
          className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${getRankColor(
            rank
          )}`}
        >
          {getRankIcon(rank)}
        </div>

        {/* Team Color Bar */}
        <div
          className="w-1 h-16 rounded-full"
          style={{ backgroundColor: team.color }}
        />

        {/* Team Info */}
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">{team.name}</h3>
          {team.description && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{team.description}</p>
          )}
          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600 dark:text-gray-400">
            <span className="flex items-center space-x-1">
              <Users size={14} />
              <span>{team.member_count} members</span>
            </span>
            {team.achievement_count > 0 && (
              <span className="flex items-center space-x-1">
                <Award size={14} />
                <span>{team.achievement_count} achievements</span>
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
              className="w-8 h-8 animate-wiggle"
            />
            <motion.span
              key={team.total_coins}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              className="text-3xl font-bold text-llama-gold"
            >
              {team.total_coins.toLocaleString()}
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
        entity={team}
        type="team"
      />
    </>
  );
}
