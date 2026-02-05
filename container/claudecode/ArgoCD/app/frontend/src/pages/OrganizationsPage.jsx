import { Routes, Route } from 'react-router-dom'
import OrganizationList from '../components/organizations/OrganizationList'
import OrganizationForm from '../components/organizations/OrganizationForm'
import OrganizationDetail from '../components/organizations/OrganizationDetail'

function OrganizationsPage() {
  return (
    <div className="card">
      <div className="card-body">
        <Routes>
          <Route index element={<OrganizationList />} />
          <Route path="new" element={<OrganizationForm />} />
          <Route path=":id" element={<OrganizationDetail />} />
          <Route path=":id/edit" element={<OrganizationForm />} />
        </Routes>
      </div>
    </div>
  )
}

export default OrganizationsPage
