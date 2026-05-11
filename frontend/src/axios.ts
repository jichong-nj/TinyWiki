import axios from 'axios'

const instance = axios.create({
  baseURL: '/api',
  timeout: 120000, // 120 秒 = 2 分钟，给 LLM 足够的响应时间
})

// 请求拦截器：自动设置Content-Type
instance.interceptors.request.use(
  config => {
    // 如果是FormData，不要设置Content-Type，让浏览器自动处理
    if (!(config.data instanceof FormData)) {
      config.headers = config.headers || {}
      config.headers['Content-Type'] = 'application/json'
    }
    // 添加认证token
    const token = localStorage.getItem('accessToken')
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
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance
