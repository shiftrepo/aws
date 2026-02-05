import { NavLink } from 'react-router-dom'

function Navigation() {
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
      </div>
    </nav>
  )
}

export default Navigation
