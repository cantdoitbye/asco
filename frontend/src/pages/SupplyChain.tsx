import { useState } from 'react'
import { CheckCircle } from 'lucide-react'
import api from '../lib/api'
import { Card } from '../components/common/Card'
import Button from '../components/common/Button'

interface RouteRequest {
  warehouse_id: number
  anganwadi_center_ids: number[]
  vehicle_capacity_kg: number
  priority: 'balanced' | 'speed' | 'efficiency'
}

interface OptimizeResponse {
  optimized_routes: any[]
  total_distance_km: number
  estimated_time_minutes: number
  recommendations: string[]
}

const SupplyChainPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OptimizeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [request, setRequest] = useState<RouteRequest>({
    warehouse_id: 1,
    anganwadi_center_ids: [1, 2, 3],
    vehicle_capacity_kg: 500,
    priority: 'balanced'
  })

  const handleOptimize = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.post('/agents/route/optimize', request)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to optimize route')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Route Optimization</h1>
        <p className="text-gray-600">AI-powered route planning and optimization</p>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded">{error}</div>
      )}

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Configure Route</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Warehouse ID</label>
            <input
              type="number"
              value={request.warehouse_id}
              onChange={(e) => setRequest({ ...request, warehouse_id: parseInt(e.target.value) })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Vehicle Capacity (kg)</label>
            <input
              type="number"
              value={request.vehicle_capacity_kg}
              onChange={(e) => setRequest({ ...request, vehicle_capacity_kg: parseFloat(e.target.value) })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Priority</label>
            <select
              value={request.priority}
              onChange={(e) => setRequest({ ...request, priority: e.target.value as 'balanced' | 'speed' | 'efficiency' })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="balanced">Balanced</option>
              <option value="speed">Speed</option>
              <option value="efficiency">Efficiency</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700">Delivery Points (Center IDs)</label>
          <div className="flex gap-2 flex-wrap">
            {request.anganwadi_center_ids.map((id, index) => (
              <input
                key={index}
                type="number"
                value={id}
                onChange={(e) => {
                  const newIds = [...request.anganwadi_center_ids]
                  newIds[index] = parseInt(e.target.value)
                  setRequest({ ...request, anganwadi_center_ids: newIds })
                }}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            ))}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setRequest({
                ...request,
                anganwadi_center_ids: [...request.anganwadi_center_ids, 0]
              })}
            >
              Add Point
            </Button>
          </div>
        </div>

        <Button onClick={handleOptimize} disabled={loading} className="w-full mt-4">
          {loading ? 'Optimizing...' : 'Optimize Route'}
        </Button>
      </Card>

      {result && (
        <div className="mt-6 space-y-6">
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Optimization Results</h2>
            <div className="mt-4 grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{result.total_distance_km}</p>
                <p className="text-sm text-gray-500">Total Distance (km)</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{result.estimated_time_minutes}</p>
                <p className="text-sm text-gray-500">Est. Time (min)</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">{result.optimized_routes?.length || 0}</p>
                <p className="text-sm text-gray-500">Optimized Routes</p>
              </div>
            </div>

            {result.recommendations && result.recommendations.length > 0 && (
              <div className="mt-6">
                <h3 className="text-md font-semibold text-gray-900 mb-3">Recommendations</h3>
                <ul className="space-y-2">
                  {result.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>

          {result.optimized_routes?.map((route, index) => (
            <Card key={index} className="mt-4">
              <h3 className="text-md font-semibold text-gray-900">Route {index + 1}</h3>
              <pre className="mt-2 text-sm text-gray-600">{JSON.stringify(route, null, 2)}</pre>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default SupplyChainPage
