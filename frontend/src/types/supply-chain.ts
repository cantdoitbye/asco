export interface Warehouse {
  id: number
  code: string
  name: string
  district_id: number
  address?: string
  latitude?: number
  longitude?: number
  capacity_mt: number
  current_stock_mt: number
  manager_name?: string
  manager_phone?: string
  is_active: boolean
  created_at: string
}

export interface Delivery {
  id: number
  tracking_code: string
  warehouse_id: number
  anganwadi_center_id: number
  transport_fleet_id?: number
  status: string
  scheduled_date?: string
  delivered_date?: string
  total_weight_kg: number
  notes?: string
  created_at: string
  updated_at?: string
}

export interface DeliveryListResponse {
  items: Delivery[]
  total: number
  page: number
  page_size: number
}

export interface DashboardStats {
  total_anganwadi_centers: number
  total_beneficiaries: number
  total_deliveries: number
  pending_deliveries: number
  active_grievances: number
  avg_trust_score: number
  low_stock_alerts: number
  upcoming_scheduled_deliveries: number
}

export interface RecentActivity {
  id: number
  type: string
  description: string
  timestamp: string
  entity_type?: string
  entity_id?: number
}
