import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import OrganizationList from './components/OrganizationList';
import DepartmentList from './components/DepartmentList';
import UserList from './components/UserList';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <h1>Organization Management</h1>
          <ul>
            <li><Link to="/">Organizations</Link></li>
            <li><Link to="/departments">Departments</Link></li>
            <li><Link to="/users">Users</Link></li>
          </ul>
        </nav>

        <main className="content">
          <Routes>
            <Route path="/" element={<OrganizationList />} />
            <Route path="/departments" element={<DepartmentList />} />
            <Route path="/users" element={<UserList />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
