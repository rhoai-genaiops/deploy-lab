import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { getLeaderboard } from '../../services/api';
import { Users, Trophy, TrendingUp, Award } from 'lucide-react';
import TeamCard from './TeamCard';
import UserCard from './UserCard';
import ViewToggle from './ViewToggle';

export default function LeaderboardView() {
  const [viewMode, setViewMode] = useState('teams'); // 'teams' or 'users'

  const { data: teamsData, isLoading: teamsLoading } = useQuery({
    queryKey: ['leaderboard', 'teams'],
    queryFn: async () => {
      const response = await getLeaderboard.teams({ limit: 50 });
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['leaderboard', 'users'],
    queryFn: async () => {
      const response = await getLeaderboard.users({ limit: 50 });
      return response.data;
    },
    refetchInterval: 30000,
  });

  const isLoading = viewMode === 'teams' ? teamsLoading : usersLoading;
  const data = viewMode === 'teams' ? teamsData : usersData;
  const items = viewMode === 'teams' ? data?.teams : data?.users;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center space-x-3">
          <Trophy className="w-10 h-10 text-yellow-500" />
          <h2 className="text-4xl font-bold bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 bg-clip-text text-transparent">
            RDU Leaderboard
          </h2>
          <Trophy className="w-10 h-10 text-yellow-500" />
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Track the top performers earning llama-coins! 🦙
        </p>
      </div>

      {/* View Toggle */}
      <div className="flex justify-center">
        <ViewToggle viewMode={viewMode} setViewMode={setViewMode} />
      </div>

      {/* Stats Summary */}
      {!isLoading && data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              {viewMode === 'teams' ? (
                <Users className="w-5 h-5 text-blue-600" />
              ) : (
                <Users className="w-5 h-5 text-purple-600" />
              )}
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total {viewMode === 'teams' ? 'Teams' : 'Users'}
              </span>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{data.total}</p>
          </div>

          <div className="card text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <img src="/assets/llama-coin.png" className="w-5 h-5" alt="coin" />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Top Score</span>
            </div>
            <p className="text-3xl font-bold text-llama-gold">
              {items?.[0]?.total_coins || 0}
            </p>
          </div>

          <div className="card text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Award className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Achievements</span>
            </div>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              {items?.reduce((sum, item) => sum + (item.achievement_count || 0), 0) || 0}
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Leaderboard List */}
      {!isLoading && items && (
        <div className="space-y-3">
          <AnimatePresence mode="wait">
            {items.map((item, index) => (
              <motion.div
                key={viewMode === 'teams' ? item.id : item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.05 }}
              >
                {viewMode === 'teams' ? (
                  <TeamCard team={item} rank={item.rank} />
                ) : (
                  <UserCard user={item} rank={item.rank} />
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {items.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">
                No {viewMode === 'teams' ? 'teams' : 'users'} yet. Admin can add them!
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
