import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, Calendar } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getStats } from '../../services/api';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

export default function TrendModal({ isOpen, onClose, entity, type }) {
  const [period, setPeriod] = useState('30d');
  const [chartType, setChartType] = useState('area'); // 'line' or 'area'

  const { data, isLoading, error } = useQuery({
    queryKey: ['history', type, entity?.id, period],
    queryFn: async () => {
      if (type === 'user') {
        const response = await getStats.userHistory(entity.id, period);
        return response.data;
      } else {
        const response = await getStats.teamHistory(entity.id, period);
        return response.data;
      }
    },
    enabled: isOpen && !!entity,
  });

  if (!isOpen || !entity) return null;

  const periods = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' },
    { value: 'all', label: 'All Time' },
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {payload[0].payload.date}
          </p>
          <p className="text-sm text-blue-600 dark:text-blue-400">
            Daily: {payload[0].value} llama-coins
          </p>
          {payload[1] && (
            <p className="text-sm text-green-600 dark:text-green-400">
              Total: {payload[1].value} llama-coins
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div
              className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto pointer-events-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between z-10">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {entity.name}
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Performance Trends
                    </p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Close modal"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Stats Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30">
                    <p className="text-sm font-medium text-blue-700 dark:text-blue-300">
                      Current Total
                    </p>
                    <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                      {entity.total_coins?.toLocaleString() || 0}
                    </p>
                    <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                      llama-coins
                    </p>
                  </div>

                  <div className="card bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30">
                    <p className="text-sm font-medium text-green-700 dark:text-green-300">
                      Current Rank
                    </p>
                    <p className="text-3xl font-bold text-green-900 dark:text-green-100">
                      #{entity.rank}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                      position
                    </p>
                  </div>

                  <div className="card bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30">
                    <p className="text-sm font-medium text-purple-700 dark:text-purple-300">
                      Achievements
                    </p>
                    <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                      {entity.achievement_count || 0}
                    </p>
                    <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                      unlocked
                    </p>
                  </div>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap items-center justify-between gap-4">
                  {/* Period Selector */}
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    <div className="flex space-x-2">
                      {periods.map((p) => (
                        <button
                          key={p.value}
                          onClick={() => setPeriod(p.value)}
                          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                            period === p.value
                              ? 'bg-blue-600 dark:bg-blue-700 text-white'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                          }`}
                        >
                          {p.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Chart Type Toggle */}
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setChartType('area')}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        chartType === 'area'
                          ? 'bg-purple-600 dark:bg-purple-700 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      Area Chart
                    </button>
                    <button
                      onClick={() => setChartType('line')}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        chartType === 'line'
                          ? 'bg-purple-600 dark:bg-purple-700 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      Line Chart
                    </button>
                  </div>
                </div>

                {/* Chart */}
                <div className="card bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
                  {isLoading && (
                    <div className="flex items-center justify-center h-96">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    </div>
                  )}

                  {error && (
                    <div className="flex items-center justify-center h-96">
                      <p className="text-red-600 dark:text-red-400">
                        Error loading trend data: {error.message}
                      </p>
                    </div>
                  )}

                  {!isLoading && !error && data?.data && data.data.length === 0 && (
                    <div className="flex items-center justify-center h-96">
                      <div className="text-center">
                        <TrendingUp className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-500 dark:text-gray-400">
                          No transaction history for this period
                        </p>
                      </div>
                    </div>
                  )}

                  {!isLoading && !error && data?.data && data.data.length > 0 && (
                    <ResponsiveContainer width="100%" height={400}>
                      {chartType === 'area' ? (
                        <AreaChart data={data.data}>
                          <defs>
                            <linearGradient id="colorDaily" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorCumulative" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                          <XAxis
                            dataKey="date"
                            className="text-xs text-gray-600 dark:text-gray-400"
                            tick={{ fill: 'currentColor' }}
                          />
                          <YAxis className="text-xs text-gray-600 dark:text-gray-400" tick={{ fill: 'currentColor' }} />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <Area
                            type="monotone"
                            dataKey="daily_coins"
                            stroke="#3B82F6"
                            fillOpacity={1}
                            fill="url(#colorDaily)"
                            name="Daily Coins"
                          />
                          <Area
                            type="monotone"
                            dataKey="cumulative_coins"
                            stroke="#10B981"
                            fillOpacity={1}
                            fill="url(#colorCumulative)"
                            name="Total Coins"
                          />
                        </AreaChart>
                      ) : (
                        <LineChart data={data.data}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                          <XAxis
                            dataKey="date"
                            className="text-xs text-gray-600 dark:text-gray-400"
                            tick={{ fill: 'currentColor' }}
                          />
                          <YAxis className="text-xs text-gray-600 dark:text-gray-400" tick={{ fill: 'currentColor' }} />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="daily_coins"
                            stroke="#3B82F6"
                            strokeWidth={2}
                            name="Daily Coins"
                            dot={{ fill: '#3B82F6', r: 4 }}
                          />
                          <Line
                            type="monotone"
                            dataKey="cumulative_coins"
                            stroke="#10B981"
                            strokeWidth={2}
                            name="Total Coins"
                            dot={{ fill: '#10B981', r: 4 }}
                          />
                        </LineChart>
                      )}
                    </ResponsiveContainer>
                  )}
                </div>

                {/* Footer Info */}
                {!isLoading && !error && data?.data && data.data.length > 0 && (
                  <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                    Showing {data.data.length} data points over the selected period
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
