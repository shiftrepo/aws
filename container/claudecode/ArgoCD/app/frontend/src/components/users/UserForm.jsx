import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createUser, updateUser, getUserById } from '../../api/userApi'
import { getActiveOrganizations } from '../../api/organizationApi'
import { getDepartmentsByOrganization } from '../../api/departmentApi'

function UserForm() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id

  const [formData, setFormData] = useState({
    username: '',
    fullName: '',
    email: '',
    phone: '',
    position: '',
    organizationId: '',
    departmentId: '',
  })
  const [organizations, setOrganizations] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    fetchOrganizations()
  }, [])

  useEffect(() => {
    if (isEditMode) {
      fetchUser()
    }
  }, [id])

  useEffect(() => {
    if (formData.organizationId) {
      fetchDepartmentsByOrganization(formData.organizationId)
    }
  }, [formData.organizationId])

  const fetchOrganizations = async () => {
    try {
      const data = await getActiveOrganizations()
      setOrganizations(data)
    } catch (err) {
      console.error('Failed to fetch organizations:', err)
    }
  }

  const fetchUser = async () => {
    try {
      setLoading(true)
      const data = await getUserById(id)
      setFormData({
        username: data.username || '',
        fullName: data.fullName || '',
        email: data.email || '',
        phone: data.phone || '',
        position: data.position || '',
        organizationId: data.organizationId || '',
        departmentId: data.departmentId || '',
      })
    } catch (err) {
      setError(err.message || 'Failed to fetch user')
    } finally {
      setLoading(false)
    }
  }

  const fetchDepartmentsByOrganization = async (orgId) => {
    try {
      const data = await getDepartmentsByOrganization(orgId)
      setDepartments(data)
    } catch (err) {
      console.error('Failed to fetch departments:', err)
    }
  }

  const validate = () => {
    const newErrors = {}

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required'
    }

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required'
    }

    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }

    if (!formData.departmentId) {
      newErrors.departmentId = 'Department is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    try {
      setLoading(true)
      setError(null)

      const submitData = {
        ...formData,
        departmentId: parseInt(formData.departmentId),
      }

      if (isEditMode) {
        await updateUser(id, submitData)
      } else {
        await createUser(submitData)
      }

      navigate('/users')
    } catch (err) {
      setError(err.message || 'Failed to save user')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate('/users')
  }

  if (loading && isEditMode) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">{isEditMode ? 'Edit User' : 'Create User'}</h2>
      </div>

      <div className="card-body">
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username" className="form-label required">
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              className={`form-control ${errors.username ? 'error' : ''}`}
              value={formData.username}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., john.doe"
            />
            {errors.username && <div className="form-error">{errors.username}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="fullName" className="form-label required">
              Full Name
            </label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              className={`form-control ${errors.fullName ? 'error' : ''}`}
              value={formData.fullName}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., John Doe"
            />
            {errors.fullName && <div className="form-error">{errors.fullName}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              className={`form-control ${errors.email ? 'error' : ''}`}
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., john.doe@company.com"
            />
            {errors.email && <div className="form-error">{errors.email}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="phone" className="form-label">
              Phone
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              className="form-control"
              value={formData.phone}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., +1-555-0123"
            />
          </div>

          <div className="form-group">
            <label htmlFor="position" className="form-label">
              Position
            </label>
            <input
              type="text"
              id="position"
              name="position"
              className="form-control"
              value={formData.position}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., Software Engineer"
            />
          </div>

          <div className="form-group">
            <label htmlFor="organizationId" className="form-label required">
              Organization
            </label>
            <select
              id="organizationId"
              name="organizationId"
              className="form-control"
              value={formData.organizationId}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">Select an organization</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="departmentId" className="form-label required">
              Department
            </label>
            <select
              id="departmentId"
              name="departmentId"
              className={`form-control ${errors.departmentId ? 'error' : ''}`}
              value={formData.departmentId}
              onChange={handleChange}
              disabled={loading || !formData.organizationId}
            >
              <option value="">Select a department</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
            {errors.departmentId && <div className="form-error">{errors.departmentId}</div>}
            {!formData.organizationId && (
              <small className="text-muted">Select an organization first</small>
            )}
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleCancel}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UserForm
