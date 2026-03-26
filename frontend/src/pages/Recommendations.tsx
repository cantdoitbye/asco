import { useState, useEffect } from 'react'
import api from '../lib/api'

interface Recommendation {
  id: number
  title: string
  description: string
  category: string
  priority: string
  impact: string
  effort: string
  timeframe: string
  actions: string[]
  metrics: string[]
  stakeholders: string[]
  confidence: number
  status: string
  created_at: string
}

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null)
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    priority: ''
  })

  useEffect(() => {
    fetchRecommendations()
  }, [filters])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (filters.status) params.status = filters.status
      if (filters.category) params.category = filters.category
      if (filters.priority) params.priority = filters.priority

      const response = await api.get('/recommendations', { params })
      setRecommendations(response.data.recommendations || [])
    } catch (error) {
      console.error('Error fetching recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    try {
      setLoading(true)
      await api.post('/recommendations/generate', {
        context: { current_data: true },
        user_role: 'admin'
      })
      fetchRecommendations()
    } catch (error) {
      console.error('Error generating recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (id: number, status: string) => {
    try {
      await api.post(`/recommendations/${id}/action`, { action: status })
      fetchRecommendations()
      if (selectedRecommendation && selectedRecommendation.id === id) {
        setSelectedRecommendation({ ...selectedRecommendation, status })
      }
    } catch (error) {
      console.error('Error updating recommendation:', error)
    }
  }

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      operations: 'bg-blue-100 text-blue-800',
      infrastructure: 'bg-purple-100 text-purple-800',
      supply_chain: 'bg-cyan-100 text-cyan-800',
      customer_service: 'bg-pink-100 text-pink-800',
      technology: 'bg-indigo-100 text-indigo-800',
      finance: 'bg-emerald-100 text-emerald-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      dismissed: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
          <p className="text-gray-600">AI-generated insights and actionable recommendations</p>
        </div>
        <button
          onClick={handleGenerate}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          Generate New
        </button>
      </div>

      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="flex gap-4">
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="dismissed">Dismissed</option>
          </select>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Categories</option>
            <option value="operations">Operations</option>
            <option value="infrastructure">Infrastructure</option>
            <option value="supply_chain">Supply Chain</option>
            <option value="customer_service">Customer Service</option>
            <option value="technology">Technology</option>
            <option value="finance">Finance</option>
          </select>
          <select
            value={filters.priority}
            onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {selectedRecommendation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold">Recommendation Details</h2>
              <button
                onClick={() => setSelectedRecommendation(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex gap-2 flex-wrap">
                <span className={`px-2 py-1 rounded-full text-xs ${getPriorityBadge(selectedRecommendation.priority)}`}>
                  Priority: {selectedRecommendation.priority}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs ${getCategoryBadge(selectedRecommendation.category)}`}>
                  {selectedRecommendation.category}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(selectedRecommendation.status)}`}>
                  {selectedRecommendation.status}
                </span>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">{selectedRecommendation.title}</h3>
                <p className="text-gray-700">{selectedRecommendation.description}</p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2 text-sm">Impact</h3>
                  <p className="text-gray-700 capitalize">{selectedRecommendation.impact}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2 text-sm">Effort</h3>
                  <p className="text-gray-700 capitalize">{selectedRecommendation.effort}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2 text-sm">Timeframe</h3>
                  <p className="text-gray-700">{selectedRecommendation.timeframe}</p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Recommended Actions</h3>
                <ul className="list-disc list-inside space-y-1">
                  {selectedRecommendation.actions.map((action, index) => (
                    <li key={index} className="text-gray-700 text-sm">{action}</li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Success Metrics</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedRecommendation.metrics.map((metric, index) => (
                      <li key={index} className="text-gray-700 text-sm">{metric}</li>
                    ))}
                  </ul>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Stakeholders</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedRecommendation.stakeholders.map((stakeholder, index) => (
                      <li key={index} className="text-gray-700 text-sm">{stakeholder}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <h3 className="font-medium">AI Confidence</h3>
                  <span className="text-indigo-600 font-semibold">{selectedRecommendation.confidence}%</span>
                </div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{ width: `${selectedRecommendation.confidence}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex justify-between gap-3 mt-6">
              <div className="text-sm text-gray-500">
                Created: {new Date(selectedRecommendation.created_at).toLocaleDateString()}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedRecommendation(null)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Close
                </button>
                {selectedRecommendation.status === 'pending' && (
                  <>
                    <button
                      onClick={() => handleAction(selectedRecommendation.id, 'in_progress')}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Start
                    </button>
                    <button
                      onClick={() => handleAction(selectedRecommendation.id, 'dismissed')}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      Dismiss
                    </button>
                  </>
                )}
                {selectedRecommendation.status === 'in_progress' && (
                  <button
                    onClick={() => handleAction(selectedRecommendation.id, 'completed')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Complete
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <>
          {recommendations.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-500">No recommendations found. Click "Generate New" to create AI-powered recommendations.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((recommendation) => (
                <div
                  key={recommendation.id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedRecommendation(recommendation)}
                >
                  <div className="p-5">
                    <div className="flex gap-2 mb-3 flex-wrap">
                      <span className={`px-2 py-1 rounded-full text-xs ${getPriorityBadge(recommendation.priority)}`}>
                        {recommendation.priority}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs ${getCategoryBadge(recommendation.category)}`}>
                        {recommendation.category}
                      </span>
                    </div>

                    <h3 className="font-semibold text-gray-900 mb-2">{recommendation.title}</h3>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{recommendation.description}</p>

                    <div className="flex gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-500">Impact:</span>
                        <span className="ml-1 font-medium capitalize">{recommendation.impact}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Effort:</span>
                        <span className="ml-1 font-medium capitalize">{recommendation.effort}</span>
                      </div>
                    </div>

                    <div className="text-sm text-gray-500 mb-4">
                      <span className="text-gray-500">Timeframe:</span>
                      <span className="ml-1 font-medium">{recommendation.timeframe}</span>
                    </div>

                    {recommendation.actions.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs text-gray-500 mb-1">Actions:</p>
                        <ul className="text-sm text-gray-700 list-disc list-inside">
                          {recommendation.actions.slice(0, 2).map((action, index) => (
                            <li key={index} className="truncate">{action}</li>
                          ))}
                          {recommendation.actions.length > 2 && (
                            <li className="text-gray-400">+{recommendation.actions.length - 2} more</li>
                          )}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(recommendation.status)}`}>
                        {recommendation.status}
                      </span>
                      <div className="flex gap-2">
                        {recommendation.status === 'pending' && (
                          <>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleAction(recommendation.id, 'in_progress') }}
                              className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                            >
                              Start
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleAction(recommendation.id, 'completed') }}
                              className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                            >
                              Complete
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleAction(recommendation.id, 'dismissed') }}
                              className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                            >
                              Dismiss
                            </button>
                          </>
                        )}
                        {recommendation.status === 'in_progress' && (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleAction(recommendation.id, 'completed') }}
                            className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                          >
                            Complete
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
