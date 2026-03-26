import { useState, useEffect } from 'react'
import api from '../lib/api'

interface AuditLog {
  id: number
  user_id: number
  action: string
  entity_type: string
  entity_id: number
  details: string
  timestamp: string
}

interface Finding {
  id: string
  title: string
  description: string
  severity: string
}

interface ComplianceMetrics {
  data_completeness: number
  timeliness: number
  accuracy: number
}

interface ComplianceReport {
  overall_status: string
  compliance_score: number
  summary: string
  findings: Finding[]
  metrics: ComplianceMetrics
  areas_of_concern: string[]
  recommendations: string[]
}

interface ComplianceScoreComponents {
  data_completeness: number
  timeliness: number
  accuracy: number
}

interface ComplianceScore {
  entity_type: string
  entity_id: number
  compliance_score: number
  components: ComplianceScoreComponents
  status: string
}

export default function Compliance() {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [report, setReport] = useState<ComplianceReport | null>(null)
  const [, setComplianceScore] = useState<ComplianceScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date

      const [reportRes, auditRes, scoreRes] = await Promise.all([
        api.get('/compliance/report', { params }),
        api.get('/compliance/audit-log'),
        api.get('/compliance/score')
      ])

      if (reportRes.data && reportRes.data.report) {
        setReport(reportRes.data.report)
      } else if (reportRes.data) {
        setReport(reportRes.data)
      }
      if (auditRes.data && auditRes.data.logs) {
        setAuditLogs(auditRes.data.logs)
      } else if (Array.isArray(auditRes.data)) {
        setAuditLogs(auditRes.data)
      } else {
        setAuditLogs([])
      }
      if (scoreRes.data && scoreRes.data.score) {
        setComplianceScore(scoreRes.data.score)
      } else if (scoreRes.data) {
        setComplianceScore(scoreRes.data)
      }
    } catch (error) {
      console.error('Error fetching compliance data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      compliant: 'bg-green-100 text-green-800',
      non_compliant: 'bg-red-100 text-red-800',
      partial: 'bg-yellow-100 text-yellow-800',
      pending_review: 'bg-blue-100 text-blue-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800'
  }

  const getScoreColor = (scoreValue: number) => {
    if (scoreValue >= 80) return 'text-green-600'
    if (scoreValue >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getProgressColor = (value: number) => {
    if (value >= 80) return 'bg-green-500'
    if (value >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
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
          <h1 className="text-2xl font-bold text-gray-900">Compliance Dashboard</h1>
          <p className="text-gray-600">Monitor compliance status and audit logs</p>
        </div>
        <button
          onClick={fetchData}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
        >
          Refresh
        </button>
      </div>

      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="flex gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          <button
            onClick={fetchData}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
          >
            Apply Filter
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Compliance Score</h2>
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="#e5e7eb"
                  strokeWidth="12"
                  fill="none"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke={report?.compliance_score && report.compliance_score >= 80 ? '#22c55e' : report?.compliance_score && report.compliance_score >= 60 ? '#eab308' : '#ef4444'}
                  strokeWidth="12"
                  fill="none"
                  strokeDasharray={`${(report?.compliance_score || 0) * 3.52} 352`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-3xl font-bold ${getScoreColor(report?.compliance_score || 0)}`}>
                  {report?.compliance_score || 0}%
                </span>
              </div>
            </div>
          </div>
          <div className="mt-4 text-center">
            <span className={`px-3 py-1 rounded-full text-sm ${getStatusBadge(report?.overall_status || '')}`}>
              {report?.overall_status?.replace('_', ' ') || 'N/A'}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Metrics</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">Data Completeness</span>
                <span className="text-sm text-gray-500">{report?.metrics?.data_completeness || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getProgressColor(report?.metrics?.data_completeness || 0)}`}
                  style={{ width: `${report?.metrics?.data_completeness || 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">Timeliness</span>
                <span className="text-sm text-gray-500">{report?.metrics?.timeliness || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getProgressColor(report?.metrics?.timeliness || 0)}`}
                  style={{ width: `${report?.metrics?.timeliness || 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">Accuracy</span>
                <span className="text-sm text-gray-500">{report?.metrics?.accuracy || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getProgressColor(report?.metrics?.accuracy || 0)}`}
                  style={{ width: `${report?.metrics?.accuracy || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {report && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Summary</h2>
            <p className="text-gray-600">{report.summary}</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Areas of Concern</h2>
            {report.areas_of_concern && report.areas_of_concern.length > 0 ? (
              <ul className="space-y-2">
                {report.areas_of_concern.map((area, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-red-500 mr-2">⚠</span>
                    <span className="text-gray-600">{area}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">No areas of concern identified</p>
            )}
          </div>
        </div>
      )}

      {report?.findings && Array.isArray(report.findings) && report.findings.length > 0 && (
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Findings</h2>
          <div className="space-y-4">
            {report.findings.map((finding: Finding) => (
              <div key={finding.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900">{finding.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs ${getSeverityBadge(finding.severity)}`}>
                    {finding.severity}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{finding.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Audit Log</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Action
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Entity Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Details
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {auditLogs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {log.user_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {log.action}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {log.entity_type}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                  {log.details}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {auditLogs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No audit logs found</p>
          </div>
        )}
      </div>
    </div>
  )
}
