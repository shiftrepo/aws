import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getUsers, deleteUser } from '../../api/userApi'

function UserList() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [totalElements, setTotalElements] = useState(0)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const size = 10

  useEffect(() => {
    fetchUsers()
  }, [page, search])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getUsers(page, size, search)
      setUsers(data.content || [])
      setTotalPages(data.totalPages || 0)
      setTotalElements(data.totalElements || 0)
    } catch (err) {
      setError(err.message || 'Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(0)
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete user "${name}"?`)) {
      return
    }

    try {
      await deleteUser(id)
      fetchUsers()
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
    return <div className="error-message">{error}</div>
  }

  return (
    <div>
      <div className="card-header">
        <h2 className="card-title">Users</h2>
        <Link to="/users/new" className="btn btn-primary">
          Add User
        </Link>
      </div>

      <div className="search-bar">
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
          <input
            type="text"
            className="form-control search-input"
            placeholder="Search users..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            Search
          </button>
          {search && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setSearchInput('')
                setSearch('')
                setPage(0)
              }}
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {users.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👤</div>
          <h3 className="empty-state-title">No Users Found</h3>
          <p className="empty-state-text">
            {search
              ? 'No users match your search criteria.'
              : 'Get started by adding your first user.'}
          </p>
          {!search && (
            <Link to="/users/new" className="btn btn-primary">
              Create User
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Department</th>
                  <th>Position</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <Link to={`/users/${user.id}`}>{user.username}</Link>
                    </td>
                    <td>{user.fullName || '-'}</td>
                    <td>{user.email || '-'}</td>
                    <td>{user.departmentName || '-'}</td>
                    <td>{user.position || '-'}</td>
                    <td>
                      <div className="table-actions">
                        <Link
                          to={`/users/${user.id}/edit`}
                          className="btn btn-sm btn-secondary"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => handleDelete(user.id, user.username)}
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

export default UserList
