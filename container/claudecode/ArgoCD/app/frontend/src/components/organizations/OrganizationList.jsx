import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getOrganizations, deleteOrganization } from '../../api/organizationApi'

function OrganizationList() {
  const [organizations, setOrganizations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [totalElements, setTotalElements] = useState(0)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const size = 10

  useEffect(() => {
    fetchOrganizations()
  }, [page, search])

  const fetchOrganizations = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getOrganizations(page, size, search)
      setOrganizations(data.content || [])
      setTotalPages(data.totalPages || 0)
      setTotalElements(data.totalElements || 0)
    } catch (err) {
      setError(err.message || 'Failed to fetch organizations')
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
    if (!window.confirm(`Are you sure you want to delete organization "${name}"?`)) {
      return
    }

    try {
      await deleteOrganization(id)
      fetchOrganizations()
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
    return <div className="error-message">{error}</div>
  }

  return (
    <div>
      <div className="card-header">
        <h2 className="card-title">Organizations</h2>
        <Link to="/organizations/new" className="btn btn-primary">
          Add Organization
        </Link>
      </div>

      <div className="search-bar">
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
          <input
            type="text"
            className="form-control search-input"
            placeholder="Search organizations..."
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

      {organizations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <h3 className="empty-state-title">No Organizations Found</h3>
          <p className="empty-state-text">
            {search
              ? 'No organizations match your search criteria.'
              : 'Get started by creating your first organization.'}
          </p>
          {!search && (
            <Link to="/organizations/new" className="btn btn-primary">
              Create Organization
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Established Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {organizations.map((org) => (
                  <tr key={org.id}>
                    <td>{org.code}</td>
                    <td>
                      <Link to={`/organizations/${org.id}`}>{org.name}</Link>
                    </td>
                    <td>{org.description || '-'}</td>
                    <td>{org.establishedDate || '-'}</td>
                    <td>
                      <span className={`badge ${org.active ? 'badge-success' : 'badge-danger'}`}>
                        {org.active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <div className="table-actions">
                        <Link
                          to={`/organizations/${org.id}/edit`}
                          className="btn btn-sm btn-secondary"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => handleDelete(org.id, org.name)}
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

export default OrganizationList
