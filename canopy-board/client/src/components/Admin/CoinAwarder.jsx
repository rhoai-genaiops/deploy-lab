import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { admin, getTeams } from '../../services/api';
import { Coins, CheckCircle, AlertCircle, Users, User } from 'lucide-react';

export default function CoinAwarder() {
  const [awardType, setAwardType] = useState('user'); // 'user' or 'team'
  const [formData, setFormData] = useState({
    user_id: '',
    team_id: '',
    amount: '',
    reason: '',
  });
  const [message, setMessage] = useState(null);
  const queryClient = useQueryClient();

  const { data: usersData } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: async () => {
      const response = await admin.users.all();
      return response.data;
    },
  });

  const { data: teamsData } = useQuery({
    queryKey: ['teams'],
    queryFn: async () => {
      const response = await getTeams.all();
      return response.data;
    },
  });

  const awardUserMutation = useMutation({
    mutationFn: (data) => admin.transactions.award(data),
    onSuccess: (response) => {
      setMessage({
        type: 'success',
        text: `Successfully awarded ${formData.amount} coins to user!`,
        achievements: response.data.new_achievements,
      });
      setFormData({ user_id: '', team_id: '', amount: '', reason: '' });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
    },
    onError: (error) => {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to award coins',
      });
    },
  });

  const awardTeamMutation = useMutation({
    mutationFn: (data) => admin.transactions.awardTeam(data),
    onSuccess: (response) => {
      setMessage({
        type: 'success',
        text: `Successfully awarded ${formData.amount} coins to team!`,
        achievements: response.data.new_achievements,
      });
      setFormData({ user_id: '', team_id: '', amount: '', reason: '' });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] });
    },
    onError: (error) => {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to award coins to team',
      });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setMessage(null);

    if (awardType === 'user') {
      awardUserMutation.mutate({
        user_id: parseInt(formData.user_id),
        amount: parseInt(formData.amount),
        reason: formData.reason,
      });
    } else {
      awardTeamMutation.mutate({
        team_id: parseInt(formData.team_id),
        amount: parseInt(formData.amount),
        reason: formData.reason,
      });
    }
  };

  const isPending = awardUserMutation.isPending || awardTeamMutation.isPending;

  return (
    <div className="card max-w-2xl mx-auto">
      <h3 className="text-2xl font-bold mb-6 flex items-center space-x-2">
        <Coins className="w-7 h-7 text-llama-gold" />
        <span>Award Llama-Coins</span>
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Award Type Toggle */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Award To
          </label>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => {
                setAwardType('user');
                setFormData({ user_id: '', team_id: '', amount: formData.amount, reason: formData.reason });
              }}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 ${
                awardType === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <User size={18} />
              <span>Individual User</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setAwardType('team');
                setFormData({ user_id: '', team_id: '', amount: formData.amount, reason: formData.reason });
              }}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 ${
                awardType === 'team'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <Users size={18} />
              <span>Entire Team</span>
            </button>
          </div>
        </div>

        {/* User/Team Selection */}
        {awardType === 'user' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select User
            </label>
            <select
              value={formData.user_id}
              onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
              className="input"
              required
            >
              <option value="">Choose a user...</option>
              {usersData?.users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.team_name})
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Team
            </label>
            <select
              value={formData.team_id}
              onChange={(e) => setFormData({ ...formData, team_id: e.target.value })}
              className="input"
              required
            >
              <option value="">Choose a team...</option>
              {teamsData?.teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Coins awarded to the team directly (not distributed to individual members)
            </p>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Amount
          </label>
          <input
            type="number"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            className="input"
            placeholder="e.g., 50"
            required
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Use positive numbers to award, negative to deduct
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Reason
          </label>
          <textarea
            value={formData.reason}
            onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
            className="input"
            rows="3"
            placeholder="e.g., Completed project milestone"
            required
          />
        </div>

        {message && (
          <div
            className={`p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
            }`}
          >
            <div
              className={`flex items-center space-x-2 ${
                message.type === 'success'
                  ? 'text-green-700 dark:text-green-400'
                  : 'text-red-700 dark:text-red-400'
              }`}
            >
              {message.type === 'success' ? (
                <CheckCircle size={20} />
              ) : (
                <AlertCircle size={20} />
              )}
              <span className="font-medium">{message.text}</span>
            </div>

            {message.achievements && (
              <div className="mt-2 space-y-1">
                {message.achievements.user && message.achievements.user.map((ach) => (
                  <p key={ach.id} className="text-sm text-green-600 dark:text-green-400">
                    🎉 Unlocked: {ach.name}!
                  </p>
                ))}
                {message.achievements.team && message.achievements.team.map((ach) => (
                  <p key={ach.id} className="text-sm text-green-600 dark:text-green-400">
                    🏆 Team unlocked: {ach.name}!
                  </p>
                ))}
              </div>
            )}
          </div>
        )}

        <button
          type="submit"
          disabled={isPending}
          className="w-full btn-primary flex items-center justify-center space-x-2"
        >
          {isPending ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Awarding...</span>
            </>
          ) : (
            <>
              <Coins size={18} />
              <span>Award Coins</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
