import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 120000, // 120 秒 = 2 分钟，给 LLM 足够的响应时间
  headers: {
    'Content-Type': 'application/json'
  }
})

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