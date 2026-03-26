import { useState, useEffect } from 'react'
import api from '../lib/api'

interface Grievance {
  id: number
  ticket_number: string
  title: string
  description: string
  category: string
  priority: string
  status: string
  ai_analysis: string | null
  sentiment_score: number | null
  created_at: string
  resolved_at: string | null
}

export default function Grievances() {
  const [grievances, setGrievances] = useState<Grievance[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [selectedGrievance, setSelectedGrievance] = useState<Grievance | null>(null)
  const [filters, setFilters] = useState({
    status: '',
    category: ''
  })
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'general',
    priority: 'medium'
  })

  useEffect(() => {
    fetchGrievances()
  }, [filters])

  const fetchGrievances = async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (filters.status) params.status = filters.status
      if (filters.category) params.category = filters.category
      
      const response = await api.get('/grievances', { params })
      setGrievances(response.data.grievances || [])
    } catch (error) {
      console.error('Error fetching grievances:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/grievances', formData)
      setShowForm(false)
      setFormData({
        title: '',
        description: '',
        category: 'general',
        priority: 'medium'
      })
      fetchGrievances()
    } catch (error) {
      console.error('Error submitting grievance:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      open: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Grievance Management</h1>
          <p className="text-gray-600">AI-powered grievance analysis and resolution</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          New Grievance
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
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Categories</option>
            <option value="supply_shortage">Supply Shortage</option>
            <option value="delivery_delay">Delivery Delay</option>
            <option value="quality_issue">Quality Issue</option>
            <option value="staff_behavior">Staff Behavior</option>
            <option value="infrastructure">Infrastructure</option>
            <option value="general">General</option>
          </select>
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">Submit New Grievance</h2>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    placeholder="Enter grievance title"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  >
                    <option value="general">General</option>
                    <option value="supply_shortage">Supply Shortage</option>
                    <option value="delivery_delay">Delivery Delay</option>
                    <option value="quality_issue">Quality Issue</option>
                    <option value="staff_behavior">Staff Behavior</option>
                    <option value="infrastructure">Infrastructure</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    rows={4}
                    placeholder="Describe the grievance in detail..."
                    required
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Submit Grievance
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selectedGrievance && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-bold">{selectedGrievance.title}</h2>
                <p className="text-sm text-gray-500">{selectedGrievance.ticket_number}</p>
              </div>
              <button
                onClick={() => setSelectedGrievance(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(selectedGrievance.status)}`}>
                  {selectedGrievance.status}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs ${getPriorityBadge(selectedGrievance.priority)}`}>
                  Priority: {selectedGrievance.priority}
                </span>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Description</h3>
                <p className="text-gray-700">{selectedGrievance.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Details</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Category:</span> {selectedGrievance.category}</p>
                    <p><span className="text-gray-500">Priority:</span> {selectedGrievance.priority}</p>
                    {selectedGrievance.sentiment_score && (
                      <p><span className="text-gray-500">Sentiment Score:</span> {selectedGrievance.sentiment_score.toFixed(2)}</p>
                    )}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Timeline</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-gray-500">Created:</span> {new Date(selectedGrievance.created_at).toLocaleDateString()}</p>
                    <p><span className="text-gray-500">Resolved:</span> {selectedGrievance.resolved_at ? new Date(selectedGrievance.resolved_at).toLocaleDateString() : 'Pending'}</p>
                  </div>
                </div>
              </div>

              {selectedGrievance.ai_analysis && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">AI Analysis</h3>
                  <p className="text-gray-700 text-sm">{selectedGrievance.ai_analysis}</p>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setSelectedGrievance(null)}
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
                  Ticket
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {grievances.map((grievance) => (
                <tr
                  key={grievance.id}
                  onClick={() => setSelectedGrievance(grievance)}
                  className="hover:bg-gray-50 cursor-pointer"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {grievance.ticket_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {grievance.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {grievance.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${getPriorityBadge(grievance.priority)}`}>
                      {grievance.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(grievance.status)}`}>
                      {grievance.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(grievance.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {grievances.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No grievances found</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
