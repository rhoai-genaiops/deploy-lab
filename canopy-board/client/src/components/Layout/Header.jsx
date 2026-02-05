import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useDarkMode } from '../../context/DarkModeContext';
import { Shield, Home, LogOut, Moon, Sun } from 'lucide-react';

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const { isDarkMode, toggleDarkMode } = useDarkMode();
  const location = useLocation();

  return (
    <header className="bg-white dark:bg-gray-800 shadow-md sticky top-0 z-50 transition-colors">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <Link to="/" className="flex items-center space-x-3 group">
            <img
              src="/assets/CAI-coin.png"
              alt="Llama Coin"
              className="w-12 h-12 transition-transform group-hover:scale-110 group-hover:rotate-12"
            />
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                RDU Leaderboard
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">Track the top contributors earning CAI-coins! 🦙</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle dark mode"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <Link
              to="/"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/'
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <Home size={20} />
              <span className="font-medium">RDU Leaderboard</span>
            </Link>

            {isAuthenticated ? (
              <>
                <Link
                  to="/admin"
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    location.pathname === '/admin'
                      ? 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Shield size={20} />
                  <span className="font-medium">Admin</span>
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                >
                  <LogOut size={20} />
                  <span className="font-medium">Logout</span>
                </button>
              </>
            ) : (
              <Link
                to="/admin"
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-600 transition-colors"
              >
                <Shield size={20} />
                <span className="font-medium">Admin Login</span>
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
