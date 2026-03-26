export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  stakeholder_id?: number
  created_at: string
  updated_at?: string
}

export type UserRole = 
  | 'STATE_ADMIN'
  | 'DISTRICT_ADMIN'
  | 'BLOCK_SUPERVISOR'
  | 'AWW'
  | 'SUPPLIER'
  | 'TRANSPORTER'

export interface LoginRequest {
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
