import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getDepartments, deleteDepartment } from '../../api/departmentApi'

function DepartmentList() {
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [totalElements, setTotalElements] = useState(0)
  const size = 10

  useEffect(() => {
    fetchDepartments()
  }, [page])

  const fetchDepartments = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getDepartments(page, size)
      setDepartments(data.content || [])
      setTotalPages(data.totalPages || 0)
      setTotalElements(data.totalElements || 0)
    } catch (err) {
      setError(err.message || 'Failed to fetch departments')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete department "${name}"?`)) {
      return
    }

    try {
      await deleteDepartment(id)
      fetchDepartments()
    } catch (err) {
      alert(err.message || 'Failed to delete department')
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
    return <div className="error-message">{error}</div>
  }

  return (
    <div>
      <div className="card-header">
        <h2 className="card-title">Departments</h2>
        <Link to="/departments/new" className="btn btn-primary">
          Add Department
        </Link>
      </div>

      {departments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🏢</div>
          <h3 className="empty-state-title">No Departments Found</h3>
          <p className="empty-state-text">
            Get started by creating your first department.
          </p>
          <Link to="/departments/new" className="btn btn-primary">
            Create Department
          </Link>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Organization</th>
                  <th>Parent Department</th>
                  <th>Manager</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((dept) => (
                  <tr key={dept.id}>
                    <td>{dept.code}</td>
                    <td>
                      <Link to={`/departments/${dept.id}`}>{dept.name}</Link>
                    </td>
                    <td>{dept.organizationName || '-'}</td>
                    <td>{dept.parentDepartmentName || 'Root'}</td>
                    <td>{dept.managerName || '-'}</td>
                    <td>
                      <div className="table-actions">
                        <Link
                          to={`/departments/${dept.id}/edit`}
                          className="btn btn-sm btn-secondary"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => handleDelete(dept.id, dept.name)}
                          className="btn btn-sm btn-danger"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <span className="pagination-info">
              Showing {page * size + 1} to {Math.min((page + 1) * size, totalElements)} of{' '}
              {totalElements} entries
            </span>
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setPage(page - 1)}
              disabled={page === 0}
            >
              Previous
            </button>
            <span>
              Page {page + 1} of {totalPages}
            </span>
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages - 1}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default DepartmentList
