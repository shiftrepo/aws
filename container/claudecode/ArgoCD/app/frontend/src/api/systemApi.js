import axiosInstance from './axios'

/**
 * System API - Endpoints for system information and health
 */

/**
 * Get system information including pod name, session ID, Flyway version, and database status
 * @returns {Promise} Promise resolving to system info object
 */
export const getSystemInfo = () => {
  return axiosInstance.get('/api/system/info')
}
