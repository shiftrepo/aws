import React, { useState, useEffect } from 'react';
import { departmentsApi, organizationsApi } from '../api/api';

function DepartmentList() {
  const [departments, setDepartments] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    organizationId: '',
    parentDepartmentId: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [deptsResponse, orgsResponse] = await Promise.all([
        departmentsApi.getAll(),
        organizationsApi.getAll(),
      ]);
      setDepartments(deptsResponse.data);
      setOrganizations(orgsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.organizationId) {
      alert('Department name and organization are required');
      return;
    }
    try {
      const payload = {
        name: formData.name,
        description: formData.description,
        organizationId: parseInt(formData.organizationId),
        parentDepartmentId: formData.parentDepartmentId
          ? parseInt(formData.parentDepartmentId)
          : null,
      };
      await departmentsApi.create(payload);
      setFormData({ name: '', description: '', organizationId: '', parentDepartmentId: '' });
      fetchData();
    } catch (err) {
      alert('Failed to create department: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this department?')) return;
    try {
      await departmentsApi.delete(id);
      fetchData();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  const getOrganizationName = (orgId) => {
    const org = organizations.find((o) => o.id === orgId);
    return org ? org.name : 'Unknown';
  };

  const getDepartmentName = (deptId) => {
    const dept = departments.find((d) => d.id === deptId);
    return dept ? dept.name : '-';
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="department-list">
      <h2>Departments</h2>

      {/* Create Form */}
      <form onSubmit={handleCreate} className="create-form">
        <input
          type="text"
          placeholder="Department Name *"
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
        <select
          value={formData.organizationId}
          onChange={(e) => setFormData({ ...formData, organizationId: e.target.value })}
          required
        >
          <option value="">Select Organization *</option>
          {organizations.map((org) => (
            <option key={org.id} value={org.id}>
              {org.name}
            </option>
          ))}
        </select>
        <select
          value={formData.parentDepartmentId}
          onChange={(e) => setFormData({ ...formData, parentDepartmentId: e.target.value })}
        >
          <option value="">No Parent Department (Optional)</option>
          {departments.map((dept) => (
            <option key={dept.id} value={dept.id}>
              {dept.name}
            </option>
          ))}
        </select>
        <button type="submit">Create Department</button>
      </form>

      {/* List */}
      {departments.length === 0 ? (
        <p>No departments found. Create one above.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
              <th>Organization</th>
              <th>Parent Department</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept) => (
              <tr key={dept.id}>
                <td>{dept.id}</td>
                <td>{dept.name}</td>
                <td>{dept.description || '-'}</td>
                <td>{getOrganizationName(dept.organizationId)}</td>
                <td>{dept.parentDepartmentId ? getDepartmentName(dept.parentDepartmentId) : '-'}</td>
                <td>{new Date(dept.createdAt).toLocaleDateString()}</td>
                <td>
                  <button className="btn-delete" onClick={() => handleDelete(dept.id)}>
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

export default DepartmentList;
