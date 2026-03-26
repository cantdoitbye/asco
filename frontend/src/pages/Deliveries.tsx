import { useState, useEffect } from 'react'
import api from '../lib/api'
import { Card } from '../components/common/Card'
import Button from '../components/common/Button'

interface Delivery {
  id: number
  tracking_code: string
  status: string
  warehouse_id: number
  anganwadi_center_id: number
  total_weight_kg: number
  scheduled_date: string
}

const DeliveriesPage: React.FC = () => {
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchDeliveries()
  }, [])

  const fetchDeliveries = async () => {
    try {
      setLoading(true)
      const response = await api.get('/supply-chain/deliveries')
      setDeliveries(response.data.items || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmDelivery = async (deliveryId: number) => {
    try {
      await api.post(`/supply-chain/deliveries/${deliveryId}/confirm`)
      fetchDeliveries()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      scheduled: 'bg-blue-100 text-blue-800',
      in_transit: 'bg-orange-100 text-orange-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const filteredDeliveries = deliveries.filter(d => 
    searchQuery === '' || d.status.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Deliveries</h1>
          <p className="text-gray-600">Manage and track deliveries</p>
        </div>
      </div>

      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search by status..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <Button variant="secondary" onClick={() => setSearchQuery('')}>
          Clear
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
      )}

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tracking Code</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Warehouse</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Center</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Weight</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredDeliveries.map((delivery) => (
                <tr key={delivery.id}>
                  <td className="px-4 py-3 text-sm text-gray-900">{delivery.tracking_code}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(delivery.status)}`}>
                      {delivery.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{delivery.warehouse_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{delivery.anganwadi_center_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{delivery.total_weight_kg} kg</td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {delivery.scheduled_date ? new Date(delivery.scheduled_date).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => handleConfirmDelivery(delivery.id)}
                    >
                      Confirm
                    </Button>
                  </td>
                </tr>
              ))}
              {filteredDeliveries.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    No deliveries found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

export default DeliveriesPage
