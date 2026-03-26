interface PendingSyncItem {
  sync_id: string
  entity_type: string
  entity_id: number | null
  action: string
  timestamp: string
  status: string
}

interface PendingSyncListProps {
  items: PendingSyncItem[]
  onRetry: (syncId: string) => void
  onDelete: (syncId: string) => void
}

export default function PendingSyncList({ items, onRetry, onDelete }: PendingSyncListProps) {
  const getActionIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case 'create':
        return '➕'
      case 'update':
        return '✏️'
      case 'delete':
        return '🗑️'
      default:
        return '📄'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <span className="text-4xl mb-3 block">✨</span>
        <p className="text-gray-500">All data synced</p>
        <p className="text-sm text-gray-400">No pending items</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="font-medium text-gray-900">Pending Sync Items</h3>
        <p className="text-sm text-gray-500">{items.length} items waiting to sync</p>
      </div>
      
      <div className="divide-y max-h-96 overflow-y-auto">
        {items.map((item) => (
          <div key={item.sync_id} className="p-4 hover:bg-gray-50">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <span className="text-lg">{getActionIcon(item.action)}</span>
                <div>
                  <p className="font-medium text-gray-900 capitalize">
                    {item.action} {item.entity_type.replace('_', ' ')}
                  </p>
                  {item.entity_id && (
                    <p className="text-sm text-gray-500">ID: {item.entity_id}</p>
                  )}
                  <p className="text-xs text-gray-400">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
                
                {item.status === 'failed' && (
                  <button
                    onClick={() => onRetry(item.sync_id)}
                    className="text-indigo-600 hover:text-indigo-800 text-sm"
                  >
                    Retry
                  </button>
                )}
                <button
                  onClick={() => onDelete(item.sync_id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
