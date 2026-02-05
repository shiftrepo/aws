import axios from './axios'

// Get all users with pagination and search
export const getUsers = async (page = 0, size = 10, search = '') => {
  const params = { page, size }
  if (search) {
    params.search = search
  }
  const response = await axios.get('/api/users', { params })
  return response.data
}

// Get user by ID
export const getUserById = async (id) => {
  const response = await axios.get(`/api/users/${id}`)
  return response.data
}

// Get users by department
export const getUsersByDepartment = async (deptId) => {
  const response = await axios.get(`/api/users/department/${deptId}`)
  return response.data
}

// Create new user
export const createUser = async (data) => {
  const response = await axios.post('/api/users', data)
  return response.data
}

// Update user
export const updateUser = async (id, data) => {
  const response = await axios.put(`/api/users/${id}`, data)
  return response.data
}

// Delete user
export const deleteUser = async (id) => {
  const response = await axios.delete(`/api/users/${id}`)
  return response.data
}

// Get user statistics
export const getUserStats = async () => {
  try {
    const response = await axios.get('/api/users/stats')
    return response.data
  } catch (error) {
    return null
  }
}
