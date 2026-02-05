import { Routes, Route } from 'react-router-dom'
import UserList from '../components/users/UserList'
import UserForm from '../components/users/UserForm'
import UserDetail from '../components/users/UserDetail'

function UsersPage() {
  return (
    <div className="card">
      <div className="card-body">
        <Routes>
          <Route index element={<UserList />} />
          <Route path="new" element={<UserForm />} />
          <Route path=":id" element={<UserDetail />} />
          <Route path=":id/edit" element={<UserForm />} />
        </Routes>
      </div>
    </div>
  )
}

export default UsersPage
