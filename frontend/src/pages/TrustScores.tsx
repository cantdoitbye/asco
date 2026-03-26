import { useState, useEffect } from 'react'
import api from '../lib/api'

interface TrustScore {
  entity_type: string
  entity_id: number
  supplier_id?: number
  supplier_name?: string
  fleet_id?: number
  vehicle_number?: string
  center_id?: number
  center_name?: string
  user_id?: number
  user_name?: string
  score: number
  zone: string
  components: Record<string, any>
  calculated_at: string
}

export default function TrustScores() {
  const [scores, setScores] = useState<TrustScore[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedEntityType, setSelectedEntityType] = useState('')
  const [selectedZone, setSelectedZone] = useState('')
  const [zoneSummary, setZoneSummary] = useState({
    green: 0,
    yellow: 0,
    orange: 0,
    red: 0
  })
  const [selectedScore, setSelectedScore] = useState<TrustScore | null>(null)

  useEffect(() => {
    fetchScores()
  }, [selectedEntityType, selectedZone])

  const fetchScores = async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (selectedEntityType) params.entity_type = selectedEntityType
      if (selectedZone) params.zone = selectedZone
      
      const response = await api.get('/trust-scores', { params })
      setScores(response.data.scores || [])
      setZoneSummary(response.data.zone_summary || { green: 0, yellow: 0, orange: 0, red: 0 })
    } catch (error) {
      console.error('Error fetching trust scores:', error)
    } finally {
      setLoading(false)
    }
  }

  const getZoneColor = (zone: string) => {
    const colors: Record<string, string> = {
      green: 'bg-green-100 text-green-800 border-green-300',
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      orange: 'bg-orange-100 text-orange-800 border-orange-300',
      red: 'bg-red-100 text-red-800 border-red-300'
    }
    return colors[zone] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  const getEntityName = (score: TrustScore) => {
    switch (score.entity_type) {
      case 'supplier':
        return score.supplier_name || `Supplier #${score.supplier_id}`
      case 'transport_fleet':
        return score.vehicle_number || `Fleet #${score.fleet_id}`
      case 'anganwadi_center':
        return score.center_name || `Center #${score.center_id}`
      case 'supervisor':
        return score.user_name || `User #${score.user_id}`
      default:
        return `Entity #${score.entity_id}`
    }
  }

  const getScoreBar = (score: number) => {
    const percentage = (score / 5) * 100
    let color = 'bg-green-500'
    if (score < 2) color = 'bg-red-500'
    else if (score < 3) color = 'bg-orange-500'
    else if (score < 4) color = 'bg-yellow-500'
    
    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${color} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trust Score Dashboard</h1>
          <p className="text-gray-600">Ecosystem participant trust metrics</p>
        </div>
        <button
          onClick={fetchScores}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          Refresh Scores
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🟢</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Green Zone</p>
              <p className="text-2xl font-bold text-green-600">{zoneSummary.green}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🟡</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Yellow Zone</p>
              <p className="text-2xl font-bold text-yellow-600">{zoneSummary.yellow}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🟠</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Orange Zone</p>
              <p className="text-2xl font-bold text-orange-600">{zoneSummary.orange}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🔴</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Red Zone</p>
              <p className="text-2xl font-bold text-red-600">{zoneSummary.red}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="flex gap-4">
          <select
            value={selectedEntityType}
            onChange={(e) => setSelectedEntityType(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Entity Types</option>
            <option value="supplier">Suppliers</option>
            <option value="transport_fleet">Transport Fleet</option>
            <option value="anganwadi_center">Anganwadi Centers</option>
            <option value="supervisor">Supervisors</option>
          </select>
          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Zones</option>
            <option value="green">Green (4.0-5.0)</option>
            <option value="yellow">Yellow (3.0-3.9)</option>
            <option value="orange">Orange (2.0-2.9)</option>
            <option value="red">Red (0.0-1.9)</option>
          </select>
        </div>
      </div>

      {selectedScore && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold">Trust Score Details</h2>
              <button
                onClick={() => setSelectedScore(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-medium">{getEntityName(selectedScore)}</p>
                  <p className="text-sm text-gray-500">{selectedScore.entity_type.replace('_', ' ')}</p>
                </div>
                <div className={`px-4 py-2 rounded-lg border ${getZoneColor(selectedScore.zone)}`}>
                  <span className="text-2xl font-bold">{selectedScore.score.toFixed(2)}</span>
                  <span className="text-sm ml-1">/ 5.0</span>
                </div>
              </div>

              <div className="mt-4">
                <h3 className="font-medium mb-2">Score Breakdown</h3>
                {getScoreBar(selectedScore.score)}
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-3">Component Scores</h3>
                <div className="space-y-3">
                  {Object.entries(selectedScore.components || {}).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 capitalize">
                        {key.replace(/_/g, ' ').replace('score', '')}
                      </span>
                      <div className="flex items-center gap-2">
                        {typeof value === 'number' && (
                          <>
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-indigo-500 h-2 rounded-full"
                                style={{ width: `${(value / 5) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium w-16 text-right">
                              {typeof value === 'number' && value > 100 
                                ? `${value.toFixed(1)}%` 
                                : value.toFixed(2)}
                            </span>
                          </>
                        )}
                        {typeof value !== 'number' && (
                          <span className="text-sm">{String(value)}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="text-sm text-gray-500">
                Last calculated: {new Date(selectedScore.calculated_at).toLocaleString()}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setSelectedScore(null)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Zone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scores.map((score, index) => (
                <tr
                  key={`${score.entity_type}-${score.entity_id || index}`}
                  onClick={() => setSelectedScore(score)}
                  className="hover:bg-gray-50 cursor-pointer"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {getEntityName(score)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                    {score.entity_type.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold">{score.score.toFixed(2)}</span>
                      <span className="text-gray-400">/ 5.0</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getZoneColor(score.zone)}`}>
                      {score.zone.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(score.calculated_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {scores.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No trust scores found</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
