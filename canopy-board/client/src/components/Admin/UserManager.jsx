import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { admin, getTeams } from '../../services/api';
import { Plus, Trash2 } from 'lucide-react';

export default function UserManager() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', team_id: '' });
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

  const createMutation = useMutation({
    mutationFn: (data) => admin.users.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      setFormData({ name: '', email: '', team_id: '' });
      setShowForm(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => admin.users.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate({
      ...formData,
      team_id: parseInt(formData.team_id),
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-2xl font-bold">Manage Users</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Add User</span>
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h4 className="font-bold mb-4">New User</h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="text"
              placeholder="Full Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              required
            />
            <input
              type="email"
              placeholder="Email (optional)"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input"
            />
            <select
              value={formData.team_id}
              onChange={(e) => setFormData({ ...formData, team_id: e.target.value })}
              className="input"
              required
            >
              <option value="">Select Team...</option>
              {teamsData?.teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>
            <button type="submit" className="btn-primary w-full">
              Create User
            </button>
          </form>
        </div>
      )}

      <div className="grid gap-3">
        {usersData?.users.map((user) => (
          <div key={user.id} className="card flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                style={{ backgroundColor: user.team_color }}
              >
                {user.name.split(' ').map((n) => n[0]).join('').substring(0, 2)}
              </div>
              <div>
                <h4 className="font-bold">{user.name}</h4>
                <p className="text-sm text-gray-600">
                  {user.team_name} {user.email && `• ${user.email}`}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                if (confirm(`Delete user "${user.name}"?`)) {
                  deleteMutation.mutate(user.id);
                }
              }}
              className="btn-danger flex items-center space-x-2"
            >
              <Trash2 size={16} />
              <span>Delete</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
