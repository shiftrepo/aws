import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { getOrganizationById, deleteOrganization } from '../../api/organizationApi'
import { getDepartmentsByOrganization } from '../../api/departmentApi'

function OrganizationDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [organization, setOrganization] = useState(null)
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchOrganization()
    fetchDepartments()
  }, [id])

  const fetchOrganization = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getOrganizationById(id)
      setOrganization(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch organization')
    } finally {
      setLoading(false)
    }
  }

  const fetchDepartments = async () => {
    try {
      const data = await getDepartmentsByOrganization(id)
      setDepartments(data)
    } catch (err) {
      console.error('Failed to fetch departments:', err)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete organization "${organization.name}"?`)) {
      return
    }

    try {
      await deleteOrganization(id)
      navigate('/organizations')
    } catch (err) {
      alert(err.message || 'Failed to delete organization')
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-message">{error}</div>
        <Link to="/organizations" className="btn btn-secondary">
          Back to Organizations
        </Link>
      </div>
    )
  }

  if (!organization) {
    return (
      <div className="card">
        <p>Organization not found</p>
        <Link to="/organizations" className="btn btn-secondary">
          Back to Organizations
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Organization Details</h2>
          <div className="btn-group">
            <Link to={`/organizations/${id}/edit`} className="btn btn-primary">
              Edit
            </Link>
            <button onClick={handleDelete} className="btn btn-danger">
              Delete
            </button>
            <Link to="/organizations" className="btn btn-secondary">
              Back to List
            </Link>
          </div>
        </div>

        <div className="card-body">
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-label">Organization Code</div>
              <div className="detail-value">{organization.code}</div>
            </div>

            <div className="detail-item">
              <div className="detail-label">Organization Name</div>
              <div className="detail-value">{organization.name}</div>
            </div>

            <div className="detail-item">
              <div className="detail-label">Established Date</div>
              <div className="detail-value">{organization.establishedDate || '-'}</div>
            </div>

            <div className="detail-item">
              <div className="detail-label">Status</div>
              <div className="detail-value">
                <span className={`badge ${organization.active ? 'badge-success' : 'badge-danger'}`}>
                  {organization.active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>

          {organization.description && (
            <div className="detail-item" style={{ marginTop: '1rem' }}>
              <div className="detail-label">Description</div>
              <div className="detail-value">{organization.description}</div>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Departments ({departments.length})</h3>
          <Link
            to={`/departments/new?organizationId=${id}`}
            className="btn btn-primary btn-sm"
          >
            Add Department
          </Link>
        </div>

        <div className="card-body">
          {departments.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state-text">No departments in this organization yet.</p>
              <Link
                to={`/departments/new?organizationId=${id}`}
                className="btn btn-primary"
              >
                Create Department
              </Link>
            </div>
          ) : (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Parent Department</th>
                    <th>Manager</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((dept) => (
                    <tr key={dept.id}>
                      <td>{dept.code}</td>
                      <td>
                        <Link to={`/departments/${dept.id}`}>{dept.name}</Link>
                      </td>
                      <td>{dept.parentDepartmentName || 'Root'}</td>
                      <td>{dept.managerName || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default OrganizationDetail
