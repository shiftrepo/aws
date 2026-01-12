import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { organizationsApi } from '../api/api';

function OrganizationList() {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '' });

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await organizationsApi.getAll();
      setOrganizations(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch organizations: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Organization name is required');
      return;
    }
    try {
      await organizationsApi.create(formData);
      setFormData({ name: '', description: '' });
      fetchOrganizations();
    } catch (err) {
      alert('Failed to create organization: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this organization?')) return;
    try {
      await organizationsApi.delete(id);
      fetchOrganizations();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="organization-list">
      <h2>Organizations</h2>

      {/* Create Form */}
      <form onSubmit={handleCreate} className="create-form">
        <input
          type="text"
          placeholder="Organization Name *"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
        <button type="submit">Create Organization</button>
      </form>

      {/* List */}
      {organizations.length === 0 ? (
        <p>No organizations found. Create one above.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {organizations.map((org) => (
              <tr key={org.id}>
                <td>{org.id}</td>
                <td>{org.name}</td>
                <td>{org.description || '-'}</td>
                <td>{new Date(org.createdAt).toLocaleDateString()}</td>
                <td>
                  <button className="btn-delete" onClick={() => handleDelete(org.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default OrganizationList;
