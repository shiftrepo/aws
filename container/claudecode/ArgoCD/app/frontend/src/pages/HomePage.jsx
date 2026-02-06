import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getOrganizations } from '../api/organizationApi'
import { getDepartments } from '../api/departmentApi'
import { getUsers } from '../api/userApi'
import { getSystemInfo } from '../api/systemApi'

function HomePage() {
  const [stats, setStats] = useState({
    organizations: 0,
    departments: 0,
    users: 0,
  })
  const [systemInfo, setSystemInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    fetchSystemInfo()

    // Poll system info every 30 seconds
    const interval = setInterval(fetchSystemInfo, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)

      // Fetch stats from each API
      const [orgData, deptData, userData] = await Promise.all([
        getOrganizations(0, 1).catch(() => ({ totalElements: 0 })),
        getDepartments(0, 1).catch(() => ({ totalElements: 0 })),
        getUsers(0, 1).catch(() => ({ totalElements: 0 })),
      ])

      setStats({
        organizations: orgData.totalElements || 0,
        departments: deptData.totalElements || 0,
        users: userData.totalElements || 0,
      })
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSystemInfo = async () => {
    try {
      const response = await getSystemInfo()
      setSystemInfo(response.data)
    } catch (err) {
      console.error('Failed to fetch system info:', err)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="card">
        <div className="card-body">
          <h1>Welcome to Organization Management System</h1>
          <p className="text-muted">
            Manage your organizations, departments, and users efficiently in one place.
          </p>
        </div>
      </div>

      {systemInfo && (
        <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <div className="card-header">
            <h2 className="card-title" style={{ color: 'white', margin: 0 }}>System Information</h2>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', opacity: 0.9, marginBottom: '0.5rem' }}>Pod Name</div>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', fontFamily: 'monospace' }}>{systemInfo.podName}</div>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', opacity: 0.9, marginBottom: '0.5rem' }}>Session ID</div>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', fontFamily: 'monospace' }}>
                  {systemInfo.sessionId ? systemInfo.sessionId.substring(0, 8) + '...' : 'N/A'}
                </div>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', opacity: 0.9, marginBottom: '0.5rem' }}>Flyway Version</div>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', fontFamily: 'monospace' }}>V{systemInfo.flywayVersion}</div>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', opacity: 0.9, marginBottom: '0.5rem' }}>Database Status</div>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', fontFamily: 'monospace' }}>
                  {systemInfo.databaseStatus === 'OK' ? '✅ ' : '❌ '}
                  {systemInfo.databaseStatus}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card-grid">
        <div className="stat-card">
          <h3>{stats.organizations}</h3>
          <p>Organizations</p>
          <Link to="/organizations" style={{ color: 'white', marginTop: '1rem', display: 'inline-block' }}>
            View All →
          </Link>
        </div>

        <div className="stat-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
          <h3>{stats.departments}</h3>
          <p>Departments</p>
          <Link to="/departments" style={{ color: 'white', marginTop: '1rem', display: 'inline-block' }}>
            View All →
          </Link>
        </div>

        <div className="stat-card" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
          <h3>{stats.users}</h3>
          <p>Users</p>
          <Link to="/users" style={{ color: 'white', marginTop: '1rem', display: 'inline-block' }}>
            View All →
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Quick Actions</h2>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <Link to="/organizations/new" className="btn btn-primary">
              Create Organization
            </Link>
            <Link to="/departments/new" className="btn btn-success">
              Create Department
            </Link>
            <Link to="/users/new" className="btn btn-secondary">
              Add User
            </Link>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Getting Started</h2>
        </div>
        <div className="card-body">
          <ol style={{ paddingLeft: '1.5rem', lineHeight: '1.8' }}>
            <li>
              <strong>Create an Organization:</strong> Start by creating your organization structure
            </li>
            <li>
              <strong>Add Departments:</strong> Organize your company into departments and sub-departments
            </li>
            <li>
              <strong>Add Users:</strong> Add team members and assign them to departments
            </li>
            <li>
              <strong>Manage:</strong> View, edit, and manage all your organizational data
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}

export default HomePage
