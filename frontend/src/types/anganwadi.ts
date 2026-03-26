export interface AnganwadiCenter {
  id: number
  code: string
  name: string
  village_id: number
  address?: string
  latitude?: number
  longitude?: number
  aww_name?: string
  aww_phone?: string
  total_beneficiaries: number
  children_0_3: number
  children_3_6: number
  pregnant_women: number
  lactating_mothers: number
  is_active: boolean
  created_at: string
  updated_at?: string
  inventory?: Inventory[]
}

export interface District {
  id: number
  name: string
  code: string
  state: string
  created_at: string
}

export interface Block {
  id: number
  name: string
  code: string
  district_id: number
  created_at: string
}

export interface Village {
  id: number
  name: string
  code: string
  block_id: number
  latitude?: number
  longitude?: number
  population: number
  created_at: string
}

export interface AnganwadiCenterListResponse {
  items: AnganwadiCenter[]
  total: number
  page: number
  page_size: number
}

export interface Inventory {
  id: number
  item_id: number
  quantity: number
  min_threshold: number
  max_threshold: number
  last_updated: string
}
