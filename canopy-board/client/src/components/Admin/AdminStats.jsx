import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { admin } from '../../services/api';
import { Users, Trophy, Coins, TrendingUp } from 'lucide-react';
import { format } from 'date-fns';

export default function AdminStats() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async () => {
      const response = await admin.stats();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Teams</p>
              <p className="text-3xl font-bold text-blue-600">{data.total_teams}</p>
            </div>
            <Trophy className="w-12 h-12 text-blue-200" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-purple-600">{data.total_users}</p>
            </div>
            <Users className="w-12 h-12 text-purple-200" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Coins Awarded</p>
              <p className="text-3xl font-bold text-llama-gold">
                {data.total_coins_awarded.toLocaleString()}
              </p>
            </div>
            <img src="/assets/llama-coin.png" className="w-12 h-12" alt="coin" />
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
          <TrendingUp className="w-6 h-6" />
          <span>Recent Transactions</span>
        </h3>

        <div className="space-y-2">
          {data.recent_transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex-1">
                <p className="font-medium">{transaction.user_name}</p>
                <p className="text-sm text-gray-600">{transaction.reason}</p>
                <p className="text-xs text-gray-500">
                  {format(new Date(transaction.created_at), 'MMM dd, yyyy HH:mm')}
                </p>
              </div>
              <div className="text-right">
                <div className="flex items-center space-x-1">
                  <span
                    className={`text-lg font-bold ${
                      transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {transaction.amount > 0 ? '+' : ''}
                    {transaction.amount}
                  </span>
                  <img src="/assets/llama-coin.png" className="w-5 h-5" alt="coin" />
                </div>
                <span className="text-xs text-gray-500">{transaction.team_name}</span>
              </div>
            </div>
          ))}

          {data.recent_transactions.length === 0 && (
            <p className="text-center text-gray-500 py-8">No transactions yet</p>
          )}
        </div>
      </div>
    </div>
  );
}
