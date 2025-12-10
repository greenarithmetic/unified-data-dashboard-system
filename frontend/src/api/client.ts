import axios from 'axios'
import type { PaginatedResponse, StatsResponse, Record, QueryParams } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth token if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token here if needed
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    }
    return Promise.reject(error)
  }
)

export const dataApi = {
  // Get paginated data
  getData: (datasetId: string, params: QueryParams) =>
    apiClient.get<PaginatedResponse>(`/data/${datasetId}`, { params }),
  
  // Get single record
  getRecord: (datasetId: string, recordId: string) =>
    apiClient.get<Record>(`/data/${datasetId}/${recordId}`),
  
  // Get statistics
  getStats: (datasetId: string, excludeSpam: boolean = true) =>
    apiClient.get<StatsResponse>(`/data/${datasetId}/stats`, {
      params: { exclude_spam: excludeSpam },
    }),
}

export const healthApi = {
  checkHealth: () => apiClient.get('/health'),
}

export default apiClient