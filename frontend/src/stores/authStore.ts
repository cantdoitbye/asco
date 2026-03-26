import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, LoginRequest, Token } from '../types'
import api from '../lib/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post<Token>('/auth/login', credentials)
          const { access_token, user } = response.data
          set({
            user: user as User,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Login failed'
          set({
            isLoading: false,
            error: errorMessage,
          })
          throw err
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
