import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import OrganizationsPage from './pages/OrganizationsPage'
import DepartmentsPage from './pages/DepartmentsPage'
import UsersPage from './pages/UsersPage'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="organizations/*" element={<OrganizationsPage />} />
        <Route path="departments/*" element={<DepartmentsPage />} />
        <Route path="users/*" element={<UsersPage />} />
      </Route>
    </Routes>
  )
}

export default App
