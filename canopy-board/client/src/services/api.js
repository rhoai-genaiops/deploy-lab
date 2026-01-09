import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Public API calls
export const getLeaderboard = {
  users: (params) => api.get('/leaderboard/users', { params }),
  teams: (params) => api.get('/leaderboard/teams', { params }),
};

export const getStats = {
  userHistory: (userId, period = '30d') =>
    api.get(`/stats/user/${userId}/history`, { params: { period } }),
  teamHistory: (teamId, period = '30d') =>
    api.get(`/stats/team/${teamId}/history`, { params: { period } }),
};

export const getAchievements = {
  all: () => api.get('/achievements'),
  user: (userId) => api.get(`/achievements/user/${userId}`),
  team: (teamId) => api.get(`/achievements/team/${teamId}`),
};

export const getTeams = {
  all: () => api.get('/teams'),
  byId: (id) => api.get(`/teams/${id}`),
};

export const getUsers = {
  byId: (id) => api.get(`/users/${id}`),
};

// Admin API calls
export const admin = {
  login: (password) => api.post('/admin/login', { password }),
  verify: () => api.post('/admin/verify'),

  teams: {
    create: (data) => api.post('/admin/teams', data),
    update: (id, data) => api.put(`/admin/teams/${id}`, data),
    delete: (id) => api.delete(`/admin/teams/${id}`),
  },

  users: {
    all: () => api.get('/admin/users'),
    create: (data) => api.post('/admin/users', data),
    update: (id, data) => api.put(`/admin/users/${id}`, data),
    delete: (id) => api.delete(`/admin/users/${id}`),
  },

  transactions: {
    award: (data) => api.post('/admin/transactions', data),
    awardTeam: (data) => api.post('/admin/transactions/team', data),
    bulkAward: (awards) => api.post('/admin/transactions/bulk', { awards }),
  },

  achievements: {
    create: (data) => api.post('/admin/achievements', data),
    update: (id, data) => api.put(`/admin/achievements/${id}`, data),
    delete: (id) => api.delete(`/admin/achievements/${id}`),
  },

  stats: () => api.get('/admin/stats'),
};

export default api;
