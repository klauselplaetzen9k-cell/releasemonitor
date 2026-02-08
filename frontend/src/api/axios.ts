import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API helper functions
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: { email: string; password: string; first_name: string; last_name: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const projectsApi = {
  list: (params?: { skip?: number; limit?: number; source?: string; search?: string }) =>
    api.get('/projects', { params }),
  get: (id: number) => api.get(`/projects/${id}`),
  create: (data: { name: string; source: string; repo_url?: string; description?: string }) =>
    api.post('/projects', data),
  delete: (id: number) => api.delete(`/projects/${id}`),
}

export const releasesApi = {
  list: (params?: { skip?: number; limit?: number; project_id?: number; days?: number; search?: string }) =>
    api.get('/releases', { params }),
  get: (id: number) => api.get(`/releases/${id}`),
  feed: (params?: { limit?: number; days?: number }) => api.get('/releases/feed', { params }),
  getProjectReleases: (projectId: number, params?: { skip?: number; limit?: number }) =>
    api.get(`/releases/project/${projectId}`, { params }),
}

export const subscriptionsApi = {
  list: () => api.get('/subscriptions'),
  create: (data: { project_id: number; notify_email?: boolean }) => api.post('/subscriptions', data),
  update: (id: number, data: { notify_email?: boolean; notify_webhook?: boolean; webhook_url?: string }) =>
    api.put(`/subscriptions/${id}`, data),
  delete: (id: number) => api.delete(`/subscriptions/${id}`),
}
