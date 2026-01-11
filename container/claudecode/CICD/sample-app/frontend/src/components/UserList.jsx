import React, { useState, useEffect } from 'react';
import { usersApi, departmentsApi, organizationsApi } from '../api/api';

function UserList() {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    position: '',
    departmentId: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersResponse, deptsResponse, orgsResponse] = await Promise.all([
        usersApi.getAll(),
        departmentsApi.getAll(),
        organizationsApi.getAll(),
      ]);
      setUsers(usersResponse.data);
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
    if (!formData.name.trim() || !formData.email.trim() || !formData.departmentId) {
      alert('Name, email, and department are required');
      return;
    }
    try {
      const payload = {
        name: formData.name,
        email: formData.email,
        position: formData.position,
        departmentId: parseInt(formData.departmentId),
      };
      await usersApi.create(payload);
      setFormData({ name: '', email: '', position: '', departmentId: '' });
      fetchData();
    } catch (err) {
      alert('Failed to create user: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this user?')) return;
    try {
      await usersApi.delete(id);
      fetchData();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  const getDepartmentName = (deptId) => {
    const dept = departments.find((d) => d.id === deptId);
    return dept ? dept.name : 'Unknown';
  };

  const getOrganizationByDepartment = (deptId) => {
    const dept = departments.find((d) => d.id === deptId);
    if (!dept) return 'Unknown';
    const org = organizations.find((o) => o.id === dept.organizationId);
    return org ? org.name : 'Unknown';
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="user-list">
      <h2>Users</h2>

      {/* Create Form */}
      <form onSubmit={handleCreate} className="create-form">
        <input
          type="text"
          placeholder="User Name *"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
        <input
          type="email"
          placeholder="Email *"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Position (Optional)"
          value={formData.position}
          onChange={(e) => setFormData({ ...formData, position: e.target.value })}
        />
        <select
          value={formData.departmentId}
          onChange={(e) => setFormData({ ...formData, departmentId: e.target.value })}
          required
        >
          <option value="">Select Department *</option>
          {departments.map((dept) => (
            <option key={dept.id} value={dept.id}>
              {dept.name} ({getOrganizationByDepartment(dept.id)})
            </option>
          ))}
        </select>
        <button type="submit">Create User</button>
      </form>

      {/* List */}
      {users.length === 0 ? (
        <p>No users found. Create one above.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Position</th>
              <th>Department</th>
              <th>Organization</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.position || '-'}</td>
                <td>{getDepartmentName(user.departmentId)}</td>
                <td>{getOrganizationByDepartment(user.departmentId)}</td>
                <td>{new Date(user.createdAt).toLocaleDateString()}</td>
                <td>
                  <button className="btn-delete" onClick={() => handleDelete(user.id)}>
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

export default UserList;
