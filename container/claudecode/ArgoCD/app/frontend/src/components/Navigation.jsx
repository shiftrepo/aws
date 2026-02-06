import { NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getSystemInfo } from '../api/systemApi'

function Navigation() {
  const [systemInfo, setSystemInfo] = useState(null)

  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        const response = await getSystemInfo()
        setSystemInfo(response.data)
      } catch (error) {
        console.error('Failed to fetch system info:', error)
      }
    }

    fetchSystemInfo()
    const interval = setInterval(fetchSystemInfo, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          OrgMgmt System
        </NavLink>
        <ul className="navbar-menu">
          <li>
            <NavLink
              to="/organizations"
              className={({ isActive }) =>
                isActive ? 'navbar-link active' : 'navbar-link'
              }
            >
              Organizations
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/departments"
              className={({ isActive }) =>
                isActive ? 'navbar-link active' : 'navbar-link'
              }
            >
              Departments
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/users"
              className={({ isActive }) =>
                isActive ? 'navbar-link active' : 'navbar-link'
              }
            >
              Users
            </NavLink>
          </li>
        </ul>
        {systemInfo && (
          <div className="system-info">
            <span className="system-info-badge">
              <span className="system-info-label">Pod:</span> {systemInfo.podName}
            </span>
            <span className="system-info-badge">
              <span className="system-info-label">Session:</span> {systemInfo.sessionId?.substring(0, 8)}
            </span>
            <span className="system-info-badge">
              <span className="system-info-label">Flyway:</span> {systemInfo.flywayVersion}
            </span>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navigation
