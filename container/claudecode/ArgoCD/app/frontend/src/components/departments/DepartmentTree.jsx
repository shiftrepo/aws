import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getActiveOrganizations } from '../../api/organizationApi'
import { getDepartmentTree } from '../../api/departmentApi'

function DepartmentNode({ department, level = 0 }) {
  const [isExpanded, setIsExpanded] = useState(level < 2)

  const hasChildren = department.children && department.children.length > 0

  return (
    <li className="tree-item">
      <div className="tree-node" style={{ paddingLeft: `${level * 1.5}rem` }}>
        {hasChildren && (
          <button
            className="tree-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        )}
        {!hasChildren && <span style={{ width: '20px', marginRight: '0.5rem' }}></span>}
        <div className="tree-content">
          <Link to={`/departments/${department.id}`}>
            <strong>{department.name}</strong>
          </Link>
          <span className="text-muted" style={{ marginLeft: '0.5rem' }}>
            ({department.code})
          </span>
          {department.managerName && (
            <span className="text-muted" style={{ marginLeft: '0.5rem' }}>
              - {department.managerName}
            </span>
          )}
        </div>
      </div>
      {hasChildren && isExpanded && (
        <ul className="tree-children">
          {department.children.map((child) => (
            <DepartmentNode key={child.id} department={child} level={level + 1} />
          ))}
        </ul>
      )}
    </li>
  )
}

function DepartmentTree() {
  const [organizations, setOrganizations] = useState([])
  const [selectedOrgId, setSelectedOrgId] = useState('')
  const [departmentTree, setDepartmentTree] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchOrganizations()
  }, [])

  useEffect(() => {
    if (selectedOrgId) {
      fetchDepartmentTree()
    }
  }, [selectedOrgId])

  const fetchOrganizations = async () => {
    try {
      setLoading(true)
      const data = await getActiveOrganizations()
      setOrganizations(data)
      if (data.length > 0) {
        setSelectedOrgId(data[0].id)
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch organizations')
    } finally {
      setLoading(false)
    }
  }

  const fetchDepartmentTree = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getDepartmentTree(selectedOrgId)
      setDepartmentTree(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch department tree')
    } finally {
      setLoading(false)
    }
  }

  if (loading && organizations.length === 0) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return <div className="error-message">{error}</div>
  }

  if (organizations.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🏢</div>
        <h3 className="empty-state-title">No Organizations Found</h3>
        <p className="empty-state-text">
          Create an organization first before adding departments.
        </p>
        <Link to="/organizations/new" className="btn btn-primary">
          Create Organization
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="form-group">
        <label htmlFor="organization" className="form-label">
          Select Organization
        </label>
        <select
          id="organization"
          className="form-control"
          value={selectedOrgId}
          onChange={(e) => setSelectedOrgId(e.target.value)}
          style={{ maxWidth: '400px' }}
        >
          {organizations.map((org) => (
            <option key={org.id} value={org.id}>
              {org.name}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : departmentTree.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🏢</div>
          <h3 className="empty-state-title">No Departments Found</h3>
          <p className="empty-state-text">
            This organization doesn't have any departments yet.
          </p>
          <Link
            to={`/departments/new?organizationId=${selectedOrgId}`}
            className="btn btn-primary"
          >
            Create Department
          </Link>
        </div>
      ) : (
        <ul className="tree">
          {departmentTree.map((dept) => (
            <DepartmentNode key={dept.id} department={dept} />
          ))}
        </ul>
      )}
    </div>
  )
}

export default DepartmentTree
