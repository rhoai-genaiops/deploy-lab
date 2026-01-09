import React from 'react';
import { Users, UserCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ViewToggle({ viewMode, setViewMode }) {
  return (
    <div className="inline-flex bg-white rounded-lg shadow-md p-1">
      <button
        onClick={() => setViewMode('teams')}
        className={`relative px-6 py-2 rounded-lg font-medium transition-colors ${
          viewMode === 'teams'
            ? 'text-white'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        {viewMode === 'teams' && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-blue-600 rounded-lg"
            transition={{ type: 'spring', duration: 0.5 }}
          />
        )}
        <span className="relative flex items-center space-x-2">
          <Users size={20} />
          <span>Teams</span>
        </span>
      </button>

      <button
        onClick={() => setViewMode('users')}
        className={`relative px-6 py-2 rounded-lg font-medium transition-colors ${
          viewMode === 'users'
            ? 'text-white'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        {viewMode === 'users' && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-purple-600 rounded-lg"
            transition={{ type: 'spring', duration: 0.5 }}
          />
        )}
        <span className="relative flex items-center space-x-2">
          <UserCircle size={20} />
          <span>Individual</span>
        </span>
      </button>
    </div>
  );
}
