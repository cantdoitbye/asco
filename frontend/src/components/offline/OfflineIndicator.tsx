import { useState, useEffect } from 'react'

interface OfflineIndicatorProps {
  isOnline: boolean
  pendingSyncCount: number
}

export default function OfflineIndicator({ isOnline, pendingSyncCount }: OfflineIndicatorProps) {
  const [showBanner, setShowBanner] = useState(!isOnline)

  useEffect(() => {
    setShowBanner(!isOnline)
  }, [isOnline])

  if (!showBanner && isOnline) return null

  return (
    <div className={`fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 ${isOnline ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'} border rounded-lg shadow-lg p-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-orange-500'}`}></div>
          <div>
            <p className={`font-medium ${isOnline ? 'text-green-800' : 'text-orange-800'}`}>
              {isOnline ? 'Back Online' : 'You are Offline'}
            </p>
            <p className={`text-sm ${isOnline ? 'text-green-600' : 'text-orange-600'}`}>
              {isOnline 
                ? 'Syncing pending data...' 
                : `${pendingSyncCount} items pending sync`
              }
            </p>
          </div>
        </div>
        {isOnline && (
          <button
            onClick={() => setShowBanner(false)}
            className="text-green-600 hover:text-green-800"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  )
}
