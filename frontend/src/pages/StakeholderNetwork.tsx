import { useState, useEffect } from 'react'
import api from '../lib/api'

interface Stakeholder {
  id: string
  name: string
  type: string
  department: string
  role: string
  contact: string
  district_id: number | null
  block_id: number | null
  registered_at: string
}

interface Connection {
  id: string
  source: string
  target: string
  type: string
  strength: number
  created_at: string
}

interface Meeting {
  id: string
  title: string
  description: string
  scheduled_at: string
  duration_minutes: number
  location: string
  meeting_type: string
  organizer_id: number
  attendees: number[]
  status: string
}

interface NetworkData {
  stakeholders: Stakeholder[]
  connections: Connection[]
  stats: {
    total_stakeholders: number
    total_connections: number
    avg_connections: number
  }
}

export default function StakeholderNetwork() {
  const [networkData, setNetworkData] = useState<NetworkData | null>(null)
  const [meetings, setMeetings] = useState<Meeting[]>([])
    const [loading, setLoading] = useState(true)
    const [showMeetingForm, setShowMeetingForm] = useState(false)
    const [showStakeholderForm, setShowStakeholderForm] = useState(false)
    const [filters] = useState({
    type: '',
    department: ''
    })
    const [meetingFormData, setMeetingFormData] = useState({
    title: '',
    description: '',
    scheduled_at: '',
    duration_minutes: 60,
    location: '',
    meeting_type: 'in_person',
    attendees: [] as number[]
    })
    const [stakeholderFormData, setStakeholderFormData] = useState({
    name: '',
    type: 'government',
    department: '',
    role: '',
    contact: ''
  })

  useEffect(() => {
    fetchData()
  }, [filters])

  const fetchData = async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (filters.type) params.type = filters.type
      if (filters.department) params.department = filters.department

      const [networkResponse, meetingsResponse] = await Promise.all([
        api.get('/network/stakeholders', { params }),
        api.get('/network/meetings')
      ])

      const data = networkResponse.data
      if (data && data.stakeholders && Array.isArray(data.stakeholders)) {
        setNetworkData(data)
      } else {
        console.error('Invalid stakeholders data:', data)
        setNetworkData({ stakeholders: [], connections: [], stats: { total_stakeholders: 0, total_connections: 0, avg_connections: 0 } })
      }
      
      const meetingsData = meetingsResponse.data
      if (meetingsData && meetingsData.meetings && Array.isArray(meetingsData.meetings)) {
        setMeetings(meetingsData.meetings)
      } else {
        setMeetings([])
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateMeeting = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/network/meetings', meetingFormData)
      setShowMeetingForm(false)
      setMeetingFormData({
        title: '',
        description: '',
        scheduled_at: '',
        duration_minutes: 60,
        location: '',
        meeting_type: 'in_person',
        attendees: []
      })
      fetchData()
    } catch (error) {
      console.error('Error creating meeting:', error)
    }
  }

  const handleCreateStakeholder = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/network/stakeholders', stakeholderFormData)
      setShowStakeholderForm(false)
      setStakeholderFormData({
        name: '',
        type: 'government',
        department: '',
        role: '',
        contact: ''
      })
      fetchData()
    } catch (error) {
      console.error('Error creating stakeholder:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-green-100 text-green-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStakeholderById = (id: string): Stakeholder | undefined => {
    const stakeholder = networkData?.stakeholders.find(s => s.id === id)
    return stakeholder
  }
  const getStakeholderTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      government: '#3B82F6',
      healthcare: '#10B9810',
      ngo: '#8B5CF6',
      logistics: '#F59E0B',
      private: '#6B7280',
      other: '#6B7280'
    }
    return colors[type] || '#6B7280'
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stakeholder Network</h1>
          <p className="text-gray-600">Manage stakeholders, connections, and meetings</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowStakeholderForm(true)}
            className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
          >
            Add Stakeholder
          </button>
          <button
            onClick={() => setShowMeetingForm(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
          >
            Schedule Meeting
          </button>
        </div>
      </div>

      {networkData?.stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Total Stakeholders</p>
            <p className="text-2xl font-bold text-gray-900">{networkData.stats.total_stakeholders}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Total Connections</p>
            <p className="text-2xl font-bold text-gray-900">{networkData.stats.total_connections}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Avg Connections</p>
            <p className="text-2xl font-bold text-gray-900">{typeof networkData.stats.avg_connections === 'number' ? networkData.stats.avg_connections.toFixed(1) : '0.0'}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Network Graph</h2>
          <div className="h-64 overflow-auto">
            {networkData && networkData.stakeholders && networkData.stakeholders.length > 0 ? (
              <div className="space-y-4">
                {networkData.stakeholders.map((stakeholder) => (
                  <div key={stakeholder.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
                        style={{ backgroundColor: getStakeholderTypeColor(stakeholder.type) }}
                      >
                        {stakeholder.type?.charAt?.(0)?.toUpperCase?.() || '?'}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{stakeholder.name}</p>
                        <p className="text-sm text-gray-500">{stakeholder.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">{stakeholder.department}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No stakeholders found</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Connections</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strength</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {networkData?.connections && networkData.connections.length > 0 ? (
                  networkData.connections.map((connection) => (
                    <tr key={connection.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {getStakeholderById(connection.source)?.name || `ID: ${connection.source}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {getStakeholderById(connection.target)?.name || `ID: ${connection.target}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs">
                          {connection.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-indigo-600 h-2 rounded-full" 
                            style={{ width: `${(connection.strength || 0) * 10}%` }}
                          ></div>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                      No connections found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Upcoming Meetings</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {meetings && meetings.length > 0 ? (
            meetings.map((meeting) => (
              <div key={meeting.id} className="bg-white rounded-lg shadow p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">{meeting.title}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(meeting.status || 'scheduled')}`}>
                    {meeting.status || 'scheduled'}
                  </span>
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><span className="font-medium">Scheduled:</span> {new Date(meeting.scheduled_at).toLocaleString()}</p>
                  <p><span className="font-medium">Location:</span> {meeting.location}</p>
                  <p><span className="font-medium">Type:</span> {meeting.meeting_type}</p>
                  <p><span className="font-medium">Duration:</span> {meeting.duration_minutes} min</p>
                  <p><span className="font-medium">Attendees:</span> {meeting.attendees?.length || 0}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-3 text-center py-8 text-gray-500">
              No upcoming meetings
            </div>
          )}
        </div>
      </div>

      {showStakeholderForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add New Stakeholder</h2>
            <form onSubmit={handleCreateStakeholder}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={stakeholderFormData.name}
                    onChange={(e) => setStakeholderFormData({ ...stakeholderFormData, name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    value={stakeholderFormData.type}
                    onChange={(e) => setStakeholderFormData({ ...stakeholderFormData, type: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  >
                    <option value="government">Government</option>
                    <option value="healthcare">Healthcare</option>
                    <option value="ngo">NGO</option>
                    <option value="logistics">Logistics</option>
                    <option value="private">Private</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={stakeholderFormData.department}
                    onChange={(e) => setStakeholderFormData({ ...stakeholderFormData, department: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <input
                    type="text"
                    value={stakeholderFormData.role}
                    onChange={(e) => setStakeholderFormData({ ...stakeholderFormData, role: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Contact
                  </label>
                  <input
                    type="text"
                    value={stakeholderFormData.contact}
                    onChange={(e) => setStakeholderFormData({ ...stakeholderFormData, contact: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowStakeholderForm(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Add Stakeholder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showMeetingForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">Schedule New Meeting</h2>
            <form onSubmit={handleCreateMeeting}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={meetingFormData.title}
                    onChange={(e) => setMeetingFormData({ ...meetingFormData, title: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    placeholder="Enter meeting title"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={meetingFormData.description}
                    onChange={(e) => setMeetingFormData({ ...meetingFormData, description: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    rows={3}
                    placeholder="Enter meeting description"
                  ></textarea>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scheduled At
                  </label>
                  <input
                    type="datetime-local"
                    value={meetingFormData.scheduled_at}
                    onChange={(e) => setMeetingFormData({ ...meetingFormData, scheduled_at: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    value={meetingFormData.duration_minutes}
                    onChange={(e) => setMeetingFormData({ ...meetingFormData, duration_minutes: parseInt(e.target.value) })}
                    className="w-full border rounded-lg px-3 py-2"
                    min={15}
                    max={480}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={meetingFormData.location}
                    onChange={(e) => setMeetingFormData({ ...meetingFormData, location: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowMeetingForm(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Schedule Meeting
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
