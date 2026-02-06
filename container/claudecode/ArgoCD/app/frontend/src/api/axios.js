import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('authToken')
          window.location.href = '/login'
          break
        case 403:
          console.error('Access forbidden:', data.message)
          break
        case 404:
          console.error('Resource not found:', data.message)
          break
        case 500:
          console.error('Server error:', data.message)
          break
        default:
          console.error('API error:', data.message || 'Unknown error')
      }

      // Return formatted error
      return Promise.reject({
        message: data.message || `Error: ${status}`,
        status,
        data,
      })
    } else if (error.request) {
      // Request made but no response
      console.error('Network error: No response from server')
      return Promise.reject({
        message: 'Network error: Unable to reach server',
        status: 0,
      })
    } else {
      // Error setting up request
      console.error('Request error:', error.message)
      return Promise.reject({
        message: error.message || 'Request failed',
        status: 0,
      })
    }
  }
)

export default axiosInstance
