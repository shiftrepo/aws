import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  createOrganization,
  updateOrganization,
  getOrganizationById,
} from '../../api/organizationApi'

function OrganizationForm() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditMode = !!id

  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    establishedDate: '',
    active: true,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (isEditMode) {
      fetchOrganization()
    }
  }, [id])

  const fetchOrganization = async () => {
    try {
      setLoading(true)
      const data = await getOrganizationById(id)
      setFormData({
        code: data.code || '',
        name: data.name || '',
        description: data.description || '',
        establishedDate: data.establishedDate || '',
        active: data.active !== undefined ? data.active : true,
      })
    } catch (err) {
      setError(err.message || 'Failed to fetch organization')
    } finally {
      setLoading(false)
    }
  }

  const validate = () => {
    const newErrors = {}

    if (!formData.code.trim()) {
      newErrors.code = 'Organization code is required'
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Organization name is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
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

      if (isEditMode) {
        await updateOrganization(id, formData)
      } else {
        await createOrganization(formData)
      }

      navigate('/organizations')
    } catch (err) {
      setError(err.message || 'Failed to save organization')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate('/organizations')
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
          {isEditMode ? 'Edit Organization' : 'Create Organization'}
        </h2>
      </div>

      <div className="card-body">
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="code" className="form-label required">
              Organization Code
            </label>
            <input
              type="text"
              id="code"
              name="code"
              className={`form-control ${errors.code ? 'error' : ''}`}
              value={formData.code}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., ORG001"
            />
            {errors.code && <div className="form-error">{errors.code}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="name" className="form-label required">
              Organization Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              className={`form-control ${errors.name ? 'error' : ''}`}
              value={formData.name}
              onChange={handleChange}
              disabled={loading}
              placeholder="e.g., Acme Corporation"
            />
            {errors.name && <div className="form-error">{errors.name}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="description" className="form-label">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              className="form-control"
              value={formData.description}
              onChange={handleChange}
              disabled={loading}
              rows="4"
              placeholder="Brief description of the organization"
            />
          </div>

          <div className="form-group">
            <label htmlFor="establishedDate" className="form-label">
              Established Date
            </label>
            <input
              type="date"
              id="establishedDate"
              name="establishedDate"
              className="form-control"
              value={formData.establishedDate}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-checkbox">
              <input
                type="checkbox"
                name="active"
                checked={formData.active}
                onChange={handleChange}
                disabled={loading}
              />
              <span>Active</span>
            </label>
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

export default OrganizationForm
