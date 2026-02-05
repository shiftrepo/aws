import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../src/App'

// Mock the child components to avoid navigation issues in tests
jest.mock('../src/pages/HomePage', () => {
  return function HomePage() {
    return <div>Home Page</div>
  }
})

jest.mock('../src/pages/OrganizationsPage', () => {
  return function OrganizationsPage() {
    return <div>Organizations Page</div>
  }
})

jest.mock('../src/pages/DepartmentsPage', () => {
  return function DepartmentsPage() {
    return <div>Departments Page</div>
  }
})

jest.mock('../src/pages/UsersPage', () => {
  return function UsersPage() {
    return <div>Users Page</div>
  }
})

describe('App', () => {
  test('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    // Check if navigation is rendered
    expect(screen.getByText('OrgMgmt System')).toBeInTheDocument()
  })

  test('renders navigation links', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    expect(screen.getByText('Organizations')).toBeInTheDocument()
    expect(screen.getByText('Departments')).toBeInTheDocument()
    expect(screen.getByText('Users')).toBeInTheDocument()
  })

  test('renders home page by default', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    expect(screen.getByText('Home Page')).toBeInTheDocument()
  })
})
