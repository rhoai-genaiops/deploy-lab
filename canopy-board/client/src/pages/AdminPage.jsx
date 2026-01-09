import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import LoginForm from '../components/Admin/LoginForm';
import AdminPanel from '../components/Admin/AdminPanel';

export default function AdminPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto mt-12">
        <LoginForm />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <AdminPanel />
    </div>
  );
}
