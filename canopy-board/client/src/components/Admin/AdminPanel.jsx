import React, { useState } from 'react';
import { Users, Coins, Trophy, BarChart } from 'lucide-react';
import TeamManager from './TeamManager';
import UserManager from './UserManager';
import CoinAwarder from './CoinAwarder';
import AdminStats from './AdminStats';

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('stats');

  const tabs = [
    { id: 'stats', label: 'Dashboard', icon: BarChart },
    { id: 'coins', label: 'Award Coins', icon: Coins },
    { id: 'teams', label: 'Teams', icon: Trophy },
    { id: 'users', label: 'Users', icon: Users },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Admin Control Panel
        </h1>
        <p className="text-gray-600 mt-2">Manage teams, users, and award llama-coins</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md p-1">
        <div className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'stats' && <AdminStats />}
        {activeTab === 'coins' && <CoinAwarder />}
        {activeTab === 'teams' && <TeamManager />}
        {activeTab === 'users' && <UserManager />}
      </div>
    </div>
  );
}
