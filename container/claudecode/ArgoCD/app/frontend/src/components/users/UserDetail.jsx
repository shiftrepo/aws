import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { getUserById, deleteUser } from '../../api/userApi'

function UserDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchUser()
  }, [id])

  const fetchUser = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getUserById(id)
      setUser(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch user')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete user "${user.username}"?`)) {
      return
    }

    try {
      await deleteUser(id)
      navigate('/users')
    } catch (err) {
      alert(err.message || 'Failed to delete user')
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
        <Link to="/users" className="btn btn-secondary">
          Back to Users
        </Link>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="card">
        <p>User not found</p>
        <Link to="/users" className="btn btn-secondary">
          Back to Users
        </Link>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">User Details</h2>
        <div className="btn-group">
          <Link to={`/users/${id}/edit`} className="btn btn-primary">
            Edit
          </Link>
          <button onClick={handleDelete} className="btn btn-danger">
            Delete
          </button>
          <Link to="/users" className="btn btn-secondary">
            Back to List
          </Link>
        </div>
      </div>

      <div className="card-body">
        <div className="detail-grid">
          <div className="detail-item">
            <div className="detail-label">Username</div>
            <div className="detail-value">{user.username}</div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Full Name</div>
            <div className="detail-value">{user.fullName || '-'}</div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Email</div>
            <div className="detail-value">{user.email || '-'}</div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Phone</div>
            <div className="detail-value">{user.phone || '-'}</div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Position</div>
            <div className="detail-value">{user.position || '-'}</div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Department</div>
            <div className="detail-value">
              {user.departmentId ? (
                <Link to={`/departments/${user.departmentId}`}>
                  {user.departmentName || `Department #${user.departmentId}`}
                </Link>
              ) : (
                '-'
              )}
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Organization</div>
            <div className="detail-value">
              {user.organizationId ? (
                <Link to={`/organizations/${user.organizationId}`}>
                  {user.organizationName || `Organization #${user.organizationId}`}
                </Link>
              ) : (
                '-'
              )}
            </div>
          </div>

          {user.createdAt && (
            <div className="detail-item">
              <div className="detail-label">Created At</div>
              <div className="detail-value">
                {new Date(user.createdAt).toLocaleString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserDetail
