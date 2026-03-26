import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, RefreshCw, BarChart3 } from 'lucide-react'
import api from '../lib/api'
import { Card } from '../components/common/Card'
import Button from '../components/common/Button'

interface ForecastData {
  item_id: number
  item_name: string
  current_demand: number
  predicted_demand: number
  confidence: number
  trend: 'up' | 'down' | 'stable'
  period: string
}

interface SupplyItem {
  id: number
  code: string
  name: string
  category: string
  unit: string
}

const DemandForecastPage: React.FC = () => {
  const [forecasts, setForecasts] = useState<ForecastData[]>([])
  const [supplyItems, setSupplyItems] = useState<SupplyItem[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState('monthly')
  const [selectedItem, setSelectedItem] = useState<string>('')

  useEffect(() => {
    fetchSupplyItems()
  }, [])

  useEffect(() => {
    if (supplyItems.length > 0) {
      generateForecast()
    }
  }, [period, supplyItems.length])

  const fetchSupplyItems = async () => {
    try {
      const response = await api.get('/supply-chain/supply-items')
      setSupplyItems(response.data || [])
    } catch (err: any) {
      console.error('Failed to fetch supply items:', err)
    }
  }

  const generateForecast = async () => {
    try {
      setGenerating(true)
      setError(null)
      const forecastDays = period === 'weekly' ? 7 : period === 'monthly' ? 30 : 90
      const response = await api.post('/agents/forecast/generate', {
        forecast_days: forecastDays,
        include_seasonality: true
      })
      
      const forecastData = response.data.forecasts || response.data.demand_forecast || []
      if (Array.isArray(forecastData)) {
        setForecasts(forecastData.map((f: any, index: number) => ({
          item_id: f.item_id || index,
          item_name: f.item_name || supplyItems.find(s => s.id === f.item_id)?.name || `Item ${f.item_id}`,
          current_demand: f.current_demand || f.current_stock || 0,
          predicted_demand: f.predicted_demand || f.forecasted_demand || 0,
          confidence: f.confidence || f.confidence_score || 75,
          trend: f.trend || (f.predicted_demand > f.current_demand ? 'up' : f.predicted_demand < f.current_demand ? 'down' : 'stable'),
          period: f.period || period
        })))
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      setForecasts([])
    } finally {
      setGenerating(false)
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-5 w-5 text-green-500" />
      case 'down':
        return <TrendingDown className="h-5 w-5 text-red-500" />
      default:
        return <div className="h-5 w-5 text-gray-500 flex items-center justify-center">→</div>
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600 bg-green-100'
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
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
          <h1 className="text-2xl font-bold text-gray-900">Demand Forecast</h1>
          <p className="text-gray-600">AI-powered demand predictions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={generateForecast} disabled={generating}>
            <RefreshCw className={`h-4 w-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={generateForecast} disabled={generating}>
            Generate Forecast
          </Button>
        </div>
      </div>

      <div className="flex gap-4">
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="quarterly">Quarterly</option>
        </select>
        <select
          value={selectedItem}
          onChange={(e) => setSelectedItem(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Items</option>
          {supplyItems.map((item) => (
            <option key={item.id} value={item.id}>{item.name}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Total Items</p>
            <p className="text-3xl font-bold text-gray-900">{forecasts.length}</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Avg Confidence</p>
            <p className="text-3xl font-bold text-green-600">
              {forecasts.length > 0 
                ? (forecasts.reduce((acc, f) => acc + f.confidence, 0) / forecasts.length).toFixed(0)
                : 0}%
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Trending Up</p>
            <p className="text-3xl font-bold text-green-600">
              {forecasts.filter(f => f.trend === 'up').length}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Trending Down</p>
            <p className="text-3xl font-bold text-red-600">
              {forecasts.filter(f => f.trend === 'down').length}
            </p>
          </div>
        </Card>
      </div>

      <Card>
        {forecasts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Demand</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Predicted Demand</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trend</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {forecasts.map((forecast, index) => (
                  <tr key={index}>
                    <td className="px-4 py-3 text-sm text-gray-900">{forecast.item_name || `Item ${forecast.item_id}`}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{forecast.current_demand}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{forecast.predicted_demand}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {getTrendIcon(forecast.trend)}
                        <span className={`text-sm ${forecast.trend === 'up' ? 'text-green-600' : forecast.trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                          {forecast.trend}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(forecast.confidence)}`}>
                        {forecast.confidence}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">{forecast.period}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No forecasts available. Click "Generate Forecast" to create predictions.</p>
          </div>
        )}
      </Card>
    </div>
  )
}

export default DemandForecastPage
