import { useState } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import DepartmentList from '../components/departments/DepartmentList'
import DepartmentTree from '../components/departments/DepartmentTree'
import DepartmentForm from '../components/departments/DepartmentForm'

function DepartmentsListPage() {
  const [activeTab, setActiveTab] = useState('list')

  return (
    <div>
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'list' ? 'active' : ''}`}
          onClick={() => setActiveTab('list')}
        >
          List View
        </button>
        <button
          className={`tab ${activeTab === 'tree' ? 'active' : ''}`}
          onClick={() => setActiveTab('tree')}
        >
          Tree View
        </button>
      </div>

      {activeTab === 'list' ? <DepartmentList /> : <DepartmentTree />}
    </div>
  )
}

function DepartmentsPage() {
  const location = useLocation()
  const isFormPage = location.pathname.includes('/new') || location.pathname.includes('/edit')

  return (
    <div className="card">
      <div className="card-body">
        <Routes>
          <Route index element={<DepartmentsListPage />} />
          <Route path="new" element={<DepartmentForm />} />
          <Route path=":id/edit" element={<DepartmentForm />} />
        </Routes>
      </div>
    </div>
  )
}

export default DepartmentsPage
