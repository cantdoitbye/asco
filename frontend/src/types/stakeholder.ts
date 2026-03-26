export type StakeholderType = 
  | 'SUPPLIER'
  | 'TRANSPORT_FLEET'
  | 'AWW'
  | 'CDPO'
  | 'SUPERVISOR'
  | 'COLLECTOR'
  | 'SECRETARY'

export type TrustZone = 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED'

export interface Stakeholder {
  id: number
  name: string
  type: StakeholderType
  email?: string
  phone?: string
  address?: string
  district_id?: number
  block_id?: number
  is_active: boolean
  created_at: string
  updated_at?: string
  trust_scores?: TrustScore[]
}

export interface TrustScore {
  id: number
  stakeholder_id: number
  score: number
  zone: TrustZone
  delivery_performance: number
  quality_compliance: number
  grievance_rate: number
  data_accuracy: number
  calculated_at: string
}

export interface StakeholderListResponse {
  items: Stakeholder[]
  total: number
  page: number
  page_size: number
}
