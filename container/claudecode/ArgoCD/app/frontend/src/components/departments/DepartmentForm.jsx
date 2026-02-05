import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  createDepartment,
  updateDepartment,
  getDepartmentById,
  getDepartmentsByOrganization,
} from '../../api/departmentApi'
import { getActiveOrganizations } from '../../api/organizationApi'

function DepartmentForm() {
  const navigate = useNavigate()
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const isEditMode = !!id

  const [formData, setFormData] = useState({
    code: '',
    name: '',
    organizationId: searchParams.get('organizationId') || '',
    parentDepartmentId: '',
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
      fetchDepartment()
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

  const fetchDepartment = async () => {
    try {
      setLoading(true)
      const data = await getDepartmentById(id)
      setFormData({
        code: data.code || '',
        name: data.name || '',
        organizationId: data.organizationId || '',
        parentDepartmentId: data.parentDepartmentId || '',
      })
    } catch (err) {
      setError(err.message || 'Failed to fetch department')
    } finally {
      setLoading(false)
    }
  }

  const fetchDepartmentsByOrganization = async (orgId) => {
    try {
      const data = await getDepartmentsByOrganization(orgId)
      // Filter out current department if editing to prevent self-reference
      const filtered = isEditMode ? data.filter((d) => d.id !== parseInt(id)) : data
      setDepartments(filtered)
    } catch (err) {
      console.error('Failed to fetch departments:', err)
    }
  }

  const validate = () => {
    const newErrors = {}

    if (!formData.code.trim()) {
      newErrors.code = 'Department code is required'
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Department name is required'
    }

    if (!formData.organizationId) {
      newErrors.organizationId = 'Organization is required'
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
        organizationId: parseInt(formData.organizationId),
        parentDepartmentId: formData.parentDepartmentId
          ? parseInt(formData.parentDepartmentId)
          : null,
      }

      if (isEditMode) {
        await updateDepartment(id, submitData)
      } else {
        await createDepartment(submitData)
      }

      navigate('/departments')
    } catch (err) {
      setError(err.message || 'Failed to save department')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate('/departments')
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
        <h2 className="card-title">
          {isEditMode ? 'Edit Department' : 'Create Department'}
        </h2>
      </div>

      <div className="card-body">
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="organizationId" className="form-label required">
              Organization
            </label>
            <select
              id="organizationId"
              name="organizationId"
              className={`form-control ${errors.organizationId ? 'error' : ''}`}
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
            {errors.organizationId && (
              <div className="form-error">{errors.organizationId}</div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="code" className="form-label required">
              Department Code
            </label>
            <input
              type="text"
              id="code"
              name="code"
              className={`form-control ${errors.code ? 'error' : ''}`}
              value={formData.code}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., DEPT001"
            />
            {errors.code && <div className="form-error">{errors.code}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="name" className="form-label required">
              Department Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              className={`form-control ${errors.name ? 'error' : ''}`}
              value={formData.name}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., Engineering"
            />
            {errors.name && <div className="form-error">{errors.name}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="parentDepartmentId" className="form-label">
              Parent Department (Optional)
            </label>
            <select
              id="parentDepartmentId"
              name="parentDepartmentId"
              className="form-control"
              value={formData.parentDepartmentId}
              onChange={handleChange}
              disabled={loading || !formData.organizationId}
            >
              <option value="">None (Root Department)</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
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

export default DepartmentForm
