import { useState, useEffect } from 'react'

interface SyncStatusProps {
  lastSyncTime: Date | null
  isSyncing: boolean
  pendingCount: number
  onSync: () => void
}

export default function SyncStatus({ lastSyncTime, isSyncing, pendingCount, onSync }: SyncStatusProps) {
  const [timeSinceSync, setTimeSinceSync] = useState('')

  useEffect(() => {
    const updateTime = () => {
      if (!lastSyncTime) {
        setTimeSinceSync('Never')
        return
      }
      
      const now = new Date()
      const diff = now.getTime() - lastSyncTime.getTime()
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(minutes / 60)
      
      if (hours > 0) {
        setTimeSinceSync(`${hours}h ${minutes % 60}m ago`)
      } else if (minutes > 0) {
        setTimeSinceSync(`${minutes}m ago`)
      } else {
        setTimeSinceSync('Just now')
      }
    }
    
    updateTime()
    const interval = setInterval(updateTime, 60000)
    return () => clearInterval(interval)
  }, [lastSyncTime])

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isSyncing ? 'bg-blue-100' : pendingCount > 0 ? 'bg-orange-100' : 'bg-green-100'}`}>
            {isSyncing ? (
              <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : pendingCount > 0 ? (
              <span className="text-orange-600 text-lg">⏳</span>
            ) : (
              <span className="text-green-600 text-lg">✓</span>
            )}
          </div>
          <div>
            <p className="font-medium text-gray-900">
              {isSyncing ? 'Syncing...' : 'Sync Status'}
            </p>
            <p className="text-sm text-gray-500">
              Last sync: {timeSinceSync}
            </p>
          </div>
        </div>
        
        {pendingCount > 0 && !isSyncing && (
          <button
            onClick={onSync}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
          >
            Sync Now ({pendingCount})
          </button>
        )}
      </div>
      
      {pendingCount > 0 && (
        <div className="mt-3 pt-3 border-t">
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-orange-500 h-2 rounded-full"
                style={{ width: `${Math.min(pendingCount * 20, 100)}%` }}
              ></div>
            </div>
            <span className="text-sm text-gray-600">{pendingCount} pending</span>
          </div>
        </div>
      )}
    </div>
  )
}
