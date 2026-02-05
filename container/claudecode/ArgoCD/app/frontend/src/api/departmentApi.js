import axios from './axios'

// Get all departments with pagination
export const getDepartments = async (page = 0, size = 10) => {
  const response = await axios.get('/api/departments', {
    params: { page, size },
  })
  return response.data
}

// Get department by ID
export const getDepartmentById = async (id) => {
  const response = await axios.get(`/api/departments/${id}`)
  return response.data
}

// Get departments by organization
export const getDepartmentsByOrganization = async (orgId) => {
  const response = await axios.get(`/api/departments/organization/${orgId}`)
  return response.data
}

// Get root departments for an organization
export const getRootDepartments = async (orgId) => {
  const response = await axios.get(`/api/departments/organization/${orgId}/roots`)
  return response.data
}

// Get child departments of a parent
export const getChildDepartments = async (parentId) => {
  const response = await axios.get(`/api/departments/${parentId}/children`)
  return response.data
}

// Create new department
export const createDepartment = async (data) => {
  const response = await axios.post('/api/departments', data)
  return response.data
}

// Update department
export const updateDepartment = async (id, data) => {
  const response = await axios.put(`/api/departments/${id}`, data)
  return response.data
}

// Delete department
export const deleteDepartment = async (id) => {
  const response = await axios.delete(`/api/departments/${id}`)
  return response.data
}

// Get department tree for an organization
export const getDepartmentTree = async (orgId) => {
  const response = await axios.get(`/api/departments/organization/${orgId}/tree`)
  return response.data
}

// Get department statistics
export const getDepartmentStats = async () => {
  try {
    const response = await axios.get('/api/departments/stats')
    return response.data
  } catch (error) {
    return null
  }
}
