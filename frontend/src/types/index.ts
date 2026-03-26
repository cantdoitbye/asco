export * from './user'
export * from './stakeholder'
export * from './anganwadi'
export * from './supply-chain'

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
