import { Outlet } from 'react-router-dom'
import Navigation from './Navigation'

function Layout() {
  return (
    <div className="app-layout">
      <Navigation />
      <main className="main-content">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
