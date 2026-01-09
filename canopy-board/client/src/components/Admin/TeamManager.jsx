import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { admin, getTeams } from '../../services/api';
import { Plus, Edit2, Trash2 } from 'lucide-react';

export default function TeamManager() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', color: '#3B82F6' });
  const [editingId, setEditingId] = useState(null);
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ['teams'],
    queryFn: async () => {
      const response = await getTeams.all();
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => admin.teams.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
      setFormData({ name: '', description: '', color: '#3B82F6' });
      setShowForm(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => admin.teams.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-2xl font-bold">Manage Teams</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Add Team</span>
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h4 className="font-bold mb-4">New Team</h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="text"
              placeholder="Team Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              required
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Team Color</label>
              <input
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-full h-10 rounded cursor-pointer"
              />
            </div>
            <button type="submit" className="btn-primary w-full">
              Create Team
            </button>
          </form>
        </div>
      )}

      <div className="grid gap-4">
        {data?.teams.map((team) => (
          <div key={team.id} className="card flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-full" style={{ backgroundColor: team.color }} />
              <div>
                <h4 className="font-bold">{team.name}</h4>
                <p className="text-sm text-gray-600">{team.description}</p>
              </div>
            </div>
            <button
              onClick={() => {
                if (confirm(`Delete team "${team.name}"?`)) {
                  deleteMutation.mutate(team.id);
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
