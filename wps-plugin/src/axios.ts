import axios from 'axios'

// WPS 插件需要让用户配置服务器地址
const getBaseURL = (): string => {
  const stored = localStorage.getItem('tinywiki_base_url')
  return stored || 'http://localhost:8000/api'
}

const instance = axios.create({
  baseURL: getBaseURL(),
  timeout: 120000,
})

// 动态更新 baseURL
export const updateBaseURL = (url: string) => {
  instance.defaults.baseURL = url
  localStorage.setItem('tinywiki_base_url', url)
}

// 请求拦截器：自动设置Content-Type
instance.interceptors.request.use(
  config => {
    if (!(config.data instanceof FormData)) {
      config.headers = config.headers || {}
      config.headers['Content-Type'] = 'application/json'
    }
    const token = localStorage.getItem('tinywiki_access_token')
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tinywiki_access_token')
      localStorage.removeItem('tinywiki_refresh_token')
    }
    return Promise.reject(error)
  }
)

export default instance
