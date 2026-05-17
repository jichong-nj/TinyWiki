import axios from 'axios'

const instance = axios.create({
  baseURL: '/api',
  timeout: 120000,
  withCredentials: true,
})

instance.interceptors.request.use(
  config => {
    console.log('Making request to:', config.url)
    if (!(config.data instanceof FormData)) {
      config.headers = config.headers || {}
      config.headers['Content-Type'] = 'application/json'
    }
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
      console.log('Added auth header for request to:', config.url)
    } else {
      console.log('No auth token found for request to:', config.url)
    }
    return config
  },
  error => Promise.reject(error)
)

instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
    return Promise.reject(error)
  }
)

export default instance
