import { useState, useEffect, useCallback } from 'react'
import { Building2, Users, Package, AlertTriangle, Loader2, Bell, Lightbulb, Shield, Truck, Calendar, TrendingUp } from 'lucide-react'
import { Card, CardHeader, CardBody } from '../components/common'
import { useAuthStore } from '../stores/authStore'
import useWebSocket from '../hooks/useWebSocket'
import api from '../lib/api'

interface Stats {
  totalAnganwadis: number
  activeStakeholders: number
  pendingDeliveries: number
  activeAlerts: number
  complianceScore: number
  monthlyTrend: {
    anganwadis: number
    stakeholders: number
    deliveries: number
  }
}

interface Alert {
  id: string
  type: string
  title: string
  message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  created_at: string
}

interface Recommendation {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high'
  category: string
  created_at: string
}

interface ComplianceScore {
  overall: number
  categories: {
    name: string
    score: number
  }[]
  lastUpdated: string
}

interface DeliverySchedule {
  id: string
  center_name: string
  items: string
  scheduled_date: string
  status: string
}

interface Toast {
  id: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
}

interface StatsCardProps {
  title: string
  value: string | number
  icon: React.ElementType
  trend?: {
    value: number
    isPositive: boolean
  }
  color: 'blue' | 'green' | 'orange' | 'red'
}

function StatsCard({ title, value, icon: Icon, trend, color }: StatsCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
  }

  return (
    <Card>
      <CardBody className="flex items-center gap-4">
        <div className={`rounded-lg p-3 ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p
              className={`mt-1 text-sm ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}% from last month
            </p>
          )}
        </div>
      </CardBody>
    </Card>
  )
}

function CircularProgress({ value, size = 120, strokeWidth = 8 }: { value: number; size?: number; strokeWidth?: number }) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  const getColor = (score: number) => {
    if (score >= 80) return '#22c55e'
    if (score >= 60) return '#eab308'
    if (score >= 40) return '#f97316'
    return '#ef4444'
  }

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor(value)}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-gray-900">{value}%</span>
      </div>
    </div>
  )
}

function AlertsWidget({ alerts, loading }: { alerts: Alert[]; loading: boolean }) {
  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-700 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'low':
        return 'bg-green-100 text-green-700 border-green-200'
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
          <Bell className="h-5 w-5 text-gray-400" />
        </CardHeader>
        <CardBody className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
        <Bell className="h-5 w-5 text-gray-400" />
      </CardHeader>
      <CardBody className="p-0">
        {alerts.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            No active alerts
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {alerts.slice(0, 3).map((alert) => (
              <li key={alert.id} className="px-6 py-4">
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 rounded-full p-1 ${getSeverityColor(alert.severity)}`}>
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{alert.title}</p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{alert.message}</p>
                    <span className={`inline-block mt-2 px-2 py-0.5 text-xs rounded-full capitalize ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  )
}

function RecommendationsWidget({ recommendations, loading }: { recommendations: Recommendation[]; loading: boolean }) {
  const getPriorityColor = (priority: Recommendation['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700'
      case 'low':
        return 'bg-green-100 text-green-700'
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
          <Lightbulb className="h-5 w-5 text-gray-400" />
        </CardHeader>
        <CardBody className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
        <Lightbulb className="h-5 w-5 text-gray-400" />
      </CardHeader>
      <CardBody className="p-0">
        {recommendations.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            No pending recommendations
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {recommendations.slice(0, 3).map((rec) => (
              <li key={rec.id} className="px-6 py-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-full bg-purple-100 p-1">
                    <Lightbulb className="h-4 w-4 text-purple-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{rec.title}</p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{rec.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`px-2 py-0.5 text-xs rounded-full capitalize ${getPriorityColor(rec.priority)}`}>
                        {rec.priority}
                      </span>
                      <span className="text-xs text-gray-400">{rec.category}</span>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  )
}

function ComplianceWidget({ compliance, loading }: { compliance: ComplianceScore | null; loading: boolean }) {
  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Compliance Score</h3>
          <Shield className="h-5 w-5 text-gray-400" />
        </CardHeader>
        <CardBody className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        </CardBody>
      </Card>
    )
  }

  if (!compliance) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Compliance Score</h3>
          <Shield className="h-5 w-5 text-gray-400" />
        </CardHeader>
        <CardBody className="py-8 text-center text-gray-500">
          No compliance data available
        </CardBody>
      </Card>
    )
  }

  const overallScore = typeof compliance.overall === 'number' ? compliance.overall : 0
  const categories = compliance.categories || []

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Compliance Score</h3>
        <Shield className="h-5 w-5 text-gray-400" />
      </CardHeader>
      <CardBody>
        <div className="flex flex-col items-center">
          <CircularProgress value={overallScore} />
          <div className="mt-4 w-full space-y-2">
            {categories.length > 0 ? (
              categories.slice(0, 3).map((category) => (
                <div key={category.name} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{category.name}</span>
                  <span className="text-sm font-medium text-gray-900">{category.score}%</span>
                </div>
              ))
            ) : (
              <div className="text-center text-sm text-gray-500">No category data</div>
            )}
          </div>
        </div>
      </CardBody>
    </Card>
  )
}

function DeliveryScheduleWidget({ schedules, loading }: { schedules: DeliverySchedule[]; loading: boolean }) {
  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Delivery Schedule</h3>
          <Calendar className="h-5 w-5 text-gray-400" />
        </CardHeader>
        <CardBody className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        </CardBody>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Delivery Schedule</h3>
        <Calendar className="h-5 w-5 text-gray-400" />
      </CardHeader>
      <CardBody className="p-0">
        {schedules.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            No upcoming deliveries
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {schedules.slice(0, 5).map((schedule) => (
              <li key={schedule.id} className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-full bg-blue-100 p-2">
                    <Truck className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{schedule.center_name}</p>
                    <p className="text-xs text-gray-500">{schedule.items}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-900">{schedule.scheduled_date}</p>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      schedule.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                      schedule.status === 'in_transit' ? 'bg-blue-100 text-blue-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {schedule.status}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  )
}

function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
      </CardHeader>
      <CardBody>
        <div className="grid grid-cols-2 gap-3">
          <button className="rounded-lg border border-gray-200 p-4 text-left transition-colors hover:bg-gray-50">
            <Package className="mb-2 h-5 w-5 text-blue-600" />
            <p className="text-sm font-medium text-gray-900">New Shipment</p>
          </button>
          <button className="rounded-lg border border-gray-200 p-4 text-left transition-colors hover:bg-gray-50">
            <Building2 className="mb-2 h-5 w-5 text-green-600" />
            <p className="text-sm font-medium text-gray-900">Add Center</p>
          </button>
          <button className="rounded-lg border border-gray-200 p-4 text-left transition-colors hover:bg-gray-50">
            <Users className="mb-2 h-5 w-5 text-orange-600" />
            <p className="text-sm font-medium text-gray-900">Manage Users</p>
          </button>
          <button className="rounded-lg border border-gray-200 p-4 text-left transition-colors hover:bg-gray-50">
            <AlertTriangle className="mb-2 h-5 w-5 text-red-600" />
            <p className="text-sm font-medium text-gray-900">View Alerts</p>
          </button>
        </div>
      </CardBody>
    </Card>
  )
}

function ToastNotification({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 5000)
    return () => clearTimeout(timer)
  }, [onDismiss])

  const bgColor = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  }

  return (
    <div className={`${bgColor[toast.type]} text-white px-4 py-3 rounded-lg shadow-lg flex items-center justify-between`}>
      <span className="text-sm">{toast.message}</span>
      <button onClick={onDismiss} className="ml-4 text-white hover:text-gray-200">
        ×
      </button>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const { isConnected, lastMessage } = useWebSocket()

  const [stats, setStats] = useState<Stats | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [compliance, setCompliance] = useState<ComplianceScore | null>(null)
  const [deliverySchedules, setDeliverySchedules] = useState<DeliverySchedule[]>([])
  const [loading, setLoading] = useState(true)
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: Toast['type'] = 'info') => {
    const id = Date.now().toString()
    setToasts(prev => [...prev, { id, message, type }])
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const fetchDashboardStats = useCallback(async () => {
    try {
      const response = await api.get('/dashboard/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
    }
  }, [])

  const fetchAlerts = useCallback(async () => {
    try {
      const response = await api.get('/agents/supply/alerts')
      setAlerts(response.data.alerts || response.data || [])
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    }
  }, [])

  const fetchRecommendations = useCallback(async () => {
    try {
      const response = await api.get('/recommendations', { params: { status: 'pending' } })
      setRecommendations(response.data.recommendations || response.data.items || response.data || [])
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
    }
  }, [])

  const fetchComplianceScore = useCallback(async () => {
    try {
      const response = await api.get('/compliance/score')
      setCompliance(response.data)
    } catch (error) {
      console.error('Failed to fetch compliance score:', error)
    }
  }, [])

  const fetchDeliverySchedules = useCallback(async () => {
    if (user?.role !== 'AWW') return
    try {
      const response = await api.get(`/deliveries/schedule`, { params: { center_id: user.stakeholder_id } })
      setDeliverySchedules(response.data.schedules || response.data || [])
    } catch (error) {
      console.error('Failed to fetch delivery schedules:', error)
    }
  }, [user])

  const fetchAllData = useCallback(async () => {
    setLoading(true)
    await Promise.all([
      fetchDashboardStats(),
      fetchAlerts(),
      fetchRecommendations(),
      fetchComplianceScore(),
      fetchDeliverySchedules(),
    ])
    setLoading(false)
  }, [fetchDashboardStats, fetchAlerts, fetchRecommendations, fetchComplianceScore, fetchDeliverySchedules])

  useEffect(() => {
    fetchAllData()
  }, [fetchAllData])

  useEffect(() => {
    if (!lastMessage) return

    switch (lastMessage.type) {
      case 'delivery_update':
        fetchDashboardStats()
        showToast('Delivery status updated', 'info')
        break
      case 'alert_new':
        fetchAlerts()
        fetchDashboardStats()
        showToast((lastMessage.payload as { message?: string })?.message || 'New alert received', 'warning')
        break
      case 'trust_score_update':
        fetchDashboardStats()
        break
      case 'grievance_update':
        fetchDashboardStats()
        break
      case 'sync_complete':
        fetchAllData()
        showToast('Data synchronized', 'success')
        break
    }
  }, [lastMessage, fetchDashboardStats, fetchAlerts, fetchAllData, showToast])

  const getRoleBasedTitle = () => {
    switch (user?.role) {
      case 'STATE_ADMIN':
        return 'State-wide Overview'
      case 'DISTRICT_ADMIN':
        return 'District Overview'
      case 'BLOCK_SUPERVISOR':
        return 'Block Overview'
      case 'AWW':
        return 'Center Dashboard'
      case 'SUPPLIER':
        return 'Supplier Dashboard'
      case 'TRANSPORTER':
        return 'Transport Dashboard'
      default:
        return 'Dashboard'
    }
  }

  const getRoleBasedDescription = () => {
    switch (user?.role) {
      case 'STATE_ADMIN':
        return 'Monitoring supply chain operations across all districts'
      case 'DISTRICT_ADMIN':
        return 'Managing district-level supply chain operations'
      case 'BLOCK_SUPERVISOR':
        return 'Overseeing block-level Anganwadi centers'
      case 'AWW':
        return 'Your center\'s delivery and compliance status'
      case 'SUPPLIER':
        return 'Manage your supplies and deliveries'
      case 'TRANSPORTER':
        return 'Your assigned deliveries and routes'
      default:
        return 'Overview of your supply chain operations'
    }
  }

  const renderStateAdminView = () => (
    <>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Anganwadis"
          value={stats?.totalAnganwadis?.toLocaleString() ?? '-'}
          icon={Building2}
          trend={stats?.monthlyTrend?.anganwadis ? { value: stats.monthlyTrend.anganwadis, isPositive: stats.monthlyTrend.anganwadis > 0 } : undefined}
          color="blue"
        />
        <StatsCard
          title="Active Stakeholders"
          value={stats?.activeStakeholders ?? '-'}
          icon={Users}
          trend={stats?.monthlyTrend?.stakeholders ? { value: stats.monthlyTrend.stakeholders, isPositive: stats.monthlyTrend.stakeholders > 0 } : undefined}
          color="green"
        />
        <StatsCard
          title="Pending Deliveries"
          value={stats?.pendingDeliveries ?? '-'}
          icon={Package}
          trend={stats?.monthlyTrend?.deliveries ? { value: stats.monthlyTrend.deliveries, isPositive: false } : undefined}
          color="orange"
        />
        <StatsCard
          title="Active Alerts"
          value={stats?.activeAlerts ?? '-'}
          icon={AlertTriangle}
          color="red"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <ComplianceWidget compliance={compliance} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <AlertsWidget alerts={alerts} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <RecommendationsWidget recommendations={recommendations} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <QuickActions />
        </div>
      </div>
    </>
  )

  const renderDistrictAdminView = () => (
    <>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Anganwadis in District"
          value={stats?.totalAnganwadis?.toLocaleString() ?? '-'}
          icon={Building2}
          trend={stats?.monthlyTrend?.anganwadis ? { value: stats.monthlyTrend.anganwadis, isPositive: stats.monthlyTrend.anganwadis > 0 } : undefined}
          color="blue"
        />
        <StatsCard
          title="Active Stakeholders"
          value={stats?.activeStakeholders ?? '-'}
          icon={Users}
          color="green"
        />
        <StatsCard
          title="Pending Deliveries"
          value={stats?.pendingDeliveries ?? '-'}
          icon={Package}
          color="orange"
        />
        <StatsCard
          title="Active Alerts"
          value={stats?.activeAlerts ?? '-'}
          icon={AlertTriangle}
          color="red"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <AlertsWidget alerts={alerts} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <ComplianceWidget compliance={compliance} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <RecommendationsWidget recommendations={recommendations} loading={loading} />
        </div>
      </div>
    </>
  )

  const renderAWWView = () => (
    <>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Compliance Score"
          value={`${compliance?.overall ?? 0}%`}
          icon={Shield}
          color="blue"
        />
        <StatsCard
          title="Pending Deliveries"
          value={stats?.pendingDeliveries ?? '-'}
          icon={Package}
          color="orange"
        />
        <StatsCard
          title="Trust Score"
          value={stats?.complianceScore ?? '-'}
          icon={TrendingUp}
          color="green"
        />
        <StatsCard
          title="Active Alerts"
          value={stats?.activeAlerts ?? '-'}
          icon={AlertTriangle}
          color="red"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <DeliveryScheduleWidget schedules={deliverySchedules} loading={loading} />
        <AlertsWidget alerts={alerts} loading={loading} />
      </div>
    </>
  )

  const renderRoleBasedContent = () => {
    switch (user?.role) {
      case 'STATE_ADMIN':
        return renderStateAdminView()
      case 'DISTRICT_ADMIN':
      case 'BLOCK_SUPERVISOR':
        return renderDistrictAdminView()
      case 'AWW':
        return renderAWWView()
      default:
        return renderStateAdminView()
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{getRoleBasedTitle()}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {getRoleBasedDescription()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`flex items-center gap-1 text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {loading && !stats ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      ) : (
        renderRoleBasedContent()
      )}

      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <ToastNotification
            key={toast.id}
            toast={toast}
            onDismiss={() => dismissToast(toast.id)}
          />
        ))}
      </div>
    </div>
  )
}
