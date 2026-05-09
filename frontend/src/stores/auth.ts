import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '../axios'

export interface User {
  id: number
  email: string
  username: string
  avatar: string | null
  bio: string | null
  role: string
  date_joined: string
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)

  function login(email: string, password: string) {
    return axios.post('/auth/login/', { email, password })
      .then(response => {
        accessToken.value = response.data.access
        refreshToken.value = response.data.refresh
        user.value = response.data.user
        localStorage.setItem('accessToken', accessToken.value || '')
        localStorage.setItem('refreshToken', refreshToken.value || '')
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
        return response
      })
  }

  function register(email: string, username: string, password: string) {
    return axios.post('/auth/register/', { email, username, password, password_confirm: password })
      .then(response => {
        accessToken.value = response.data.access
        refreshToken.value = response.data.refresh
        user.value = response.data.user
        localStorage.setItem('accessToken', accessToken.value || '')
        localStorage.setItem('refreshToken', refreshToken.value || '')
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
        return response
      })
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    delete axios.defaults.headers.common['Authorization']
  }

  function loadFromStorage() {
    const token = localStorage.getItem('accessToken')
    const refresh = localStorage.getItem('refreshToken')
    if (token) {
      accessToken.value = token
      refreshToken.value = refresh || null
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoggedIn,
    login,
    register,
    logout,
    loadFromStorage
  }
})