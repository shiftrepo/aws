import axios from './axios'

// Get all organizations with pagination and search
export const getOrganizations = async (page = 0, size = 10, search = '') => {
  const params = { page, size }
  if (search) {
    params.search = search
  }
  const response = await axios.get('/api/organizations', { params })
  return response.data
}

// Get organization by ID
export const getOrganizationById = async (id) => {
  const response = await axios.get(`/api/organizations/${id}`)
  return response.data
}

// Create new organization
export const createOrganization = async (data) => {
  const response = await axios.post('/api/organizations', data)
  return response.data
}

// Update organization
export const updateOrganization = async (id, data) => {
  const response = await axios.put(`/api/organizations/${id}`, data)
  return response.data
}

// Delete organization
export const deleteOrganization = async (id) => {
  const response = await axios.delete(`/api/organizations/${id}`)
  return response.data
}

// Get active organizations
export const getActiveOrganizations = async () => {
  const response = await axios.get('/api/organizations/active')
  return response.data
}

// Get organization statistics
export const getOrganizationStats = async () => {
  try {
    const response = await axios.get('/api/organizations/stats')
    return response.data
  } catch (error) {
    // If stats endpoint doesn't exist, return null
    return null
  }
}
