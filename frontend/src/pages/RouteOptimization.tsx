import { useState, useEffect } from 'react'
import { Navigation, RefreshCw } from 'lucide-react'
import api from '../lib/api'
import { Card } from '../components/common/Card'
import Button from '../components/common/Button'

interface Warehouse {
  id: number
  name: string
  code: string
  district_id: number
}

interface AnganwadiCenter {
  id: number
  name: string
  code: string
  village_id: number
}

interface OptimizedRoute {
  route_id: number
  route_name: string
  total_distance_km: number
  estimated_time_minutes: number
  stops: Array<{
    center_id: number
    center_name: string
    order: number
    estimated_arrival: string
    distance_from_previous_km: number
  }>
  fuel_cost_estimate: number
  co2_emissions_estimate: number
}

const RouteOptimizationPage: React.FC = () => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [centers, setCenters] = useState<AnganwadiCenter[]>([])
  const [optimizedRoute, setOptimizedRoute] = useState<OptimizedRoute | null>(null)
  const [loading, setLoading] = useState(true)
  const [optimizing, setOptimizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('')
  const [selectedCenters, setSelectedCenters] = useState<string[]>([])
  const [vehicleCapacity, setVehicleCapacity] = useState<string>('500')
  const [priority, setPriority] = useState<string>('balanced')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [whRes, centersRes] = await Promise.all([
        api.get('/supply-chain/warehouses'),
        api.get('/anganwadi')
      ])
      setWarehouses(whRes.data || [])
      setCenters(centersRes.data.centers || centersRes.data || [])
      if (whRes.data?.length > 0) {
        setSelectedWarehouse(String(whRes.data[0].id))
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleOptimize = async () => {
    if (!selectedWarehouse || selectedCenters.length === 0) {
      setError('Please select a warehouse and at least one center')
      return
    }

    try {
      setOptimizing(true)
      setError(null)
      const response = await api.post('/agents/route/optimize', {
        warehouse_id: parseInt(selectedWarehouse),
        anganwadi_center_ids: selectedCenters.map(Number),
        vehicle_capacity_kg: parseFloat(vehicleCapacity),
        priority: priority
      })
      setOptimizedRoute(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setOptimizing(false)
    }
  }

  const toggleCenter = (centerId: string) => {
    setSelectedCenters(prev => 
      prev.includes(centerId) 
        ? prev.filter(id => id !== centerId)
        : [...prev, centerId]
    )
  }

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
          <h1 className="text-2xl font-bold text-gray-900">Route Optimization</h1>
          <p className="text-gray-600">AI-powered delivery route optimization</p>
        </div>
        <Button variant="secondary" onClick={fetchData}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Configure Route</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Warehouse
              </label>
              <select
                value={selectedWarehouse}
                onChange={(e) => setSelectedWarehouse(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="">Select Warehouse</option>
                {warehouses.map((wh) => (
                  <option key={wh.id} value={wh.id}>{wh.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vehicle Capacity (kg)
              </label>
              <input
                type="number"
                value={vehicleCapacity}
                onChange={(e) => setVehicleCapacity(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="balanced">Balanced</option>
                <option value="time">Time Priority</option>
                <option value="distance">Distance Priority</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delivery Centers ({selectedCenters.length} selected)
              </label>
              <div className="max-h-48 overflow-y-auto border rounded-lg">
                {centers.length === 0 ? (
                  <p className="p-3 text-gray-500 text-sm">No centers available</p>
                ) : (
                  centers.slice(0, 20).map((center) => (
                    <label 
                      key={center.id} 
                      className="flex items-center gap-2 p-2 hover:bg-gray-50 cursor-pointer border-b last:border-b-0"
                    >
                      <input
                        type="checkbox"
                        checked={selectedCenters.includes(String(center.id))}
                        onChange={() => toggleCenter(String(center.id))}
                        className="rounded"
                      />
                      <span className="text-sm">{center.name}</span>
                    </label>
                  ))
                )}
              </div>
            </div>

            <Button 
              onClick={handleOptimize} 
              disabled={optimizing || !selectedWarehouse || selectedCenters.length === 0}
              className="w-full"
            >
              <Navigation className="h-4 w-4 mr-2" />
              {optimizing ? 'Optimizing...' : 'Optimize Route'}
            </Button>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Optimized Route</h2>
          {optimizedRoute ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Distance</p>
                  <p className="text-xl font-semibold text-blue-700">
                    {optimizedRoute.total_distance_km?.toFixed(1) || '0'} km
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">Estimated Time</p>
                  <p className="text-xl font-semibold text-green-700">
                    {optimizedRoute.estimated_time_minutes || 0} min
                  </p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">Stops</p>
                  <p className="text-xl font-semibold text-purple-700">
                    {optimizedRoute.stops?.length || 0}
                  </p>
                </div>
              </div>

              {optimizedRoute.stops && optimizedRoute.stops.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Stop Sequence</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {optimizedRoute.stops
                      .sort((a, b) => a.order - b.order)
                      .map((stop, index) => (
                        <div key={stop.center_id || index} className="flex items-center gap-3 p-3 border rounded-lg">
                          <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-medium">
                            {index + 1}
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{stop.center_name || `Center ${stop.center_id}`}</p>
                            <p className="text-xs text-gray-500">
                              ETA: {stop.estimated_arrival || 'N/A'} • {stop.distance_from_previous_km?.toFixed(1) || 0} km from previous
                            </p>
                          </div>
                        </div>
                      ))
                    }
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Navigation className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Configure your route and click "Optimize Route" to see results</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

export default RouteOptimizationPage
