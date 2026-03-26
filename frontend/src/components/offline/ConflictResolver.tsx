import { useState } from 'react'

interface Conflict {
  field: string
  client_value: any
  server_value: any
}

interface ConflictResolverProps {
  conflicts: Conflict[]
  onResolve: (strategy: 'server_wins' | 'client_wins' | 'manual_merge', mergedData?: Record<string, any>) => void
  onClose: () => void
}

export default function ConflictResolver({ conflicts, onResolve, onClose }: ConflictResolverProps) {
  const [selectedStrategy, setSelectedStrategy] = useState<'server_wins' | 'client_wins' | 'manual_merge'>('server_wins')
  const [mergedData, setMergedData] = useState<Record<string, any>>({})

  const strategies = [
    {
      id: 'server_wins',
      name: 'Server Wins',
      description: 'Keep the server version of all conflicting data',
      icon: '🖥️'
    },
    {
      id: 'client_wins',
      name: 'Client Wins',
      description: 'Keep your local version of all conflicting data',
      icon: '📱'
    },
    {
      id: 'manual_merge',
      name: 'Manual Merge',
      description: 'Choose which values to keep for each field',
      icon: '🔀'
    }
  ]

  const handleFieldChange = (field: string, source: 'client' | 'server', value?: any) => {
    setMergedData(prev => ({
      ...prev,
      [field]: value || (source === 'client' ? conflicts.find(c => c.field === field)?.client_value : conflicts.find(c => c.field === field)?.server_value)
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Sync Conflict Detected</h2>
            <p className="text-gray-600">{conflicts.length} field(s) have conflicting values</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">Choose Resolution Strategy</h3>
          <div className="grid grid-cols-3 gap-3">
            {strategies.map((strategy) => (
              <button
                key={strategy.id}
                onClick={() => setSelectedStrategy(strategy.id as any)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  selectedStrategy === strategy.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="text-2xl mb-2 block">{strategy.icon}</span>
                <p className="font-medium text-gray-900">{strategy.name}</p>
                <p className="text-xs text-gray-500 mt-1">{strategy.description}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">Conflicting Fields</h3>
          <div className="space-y-3">
            {conflicts.map((conflict) => (
              <div key={conflict.field} className="bg-gray-50 rounded-lg p-4">
                <p className="font-medium text-gray-700 mb-2 capitalize">
                  {conflict.field.replace(/_/g, ' ')}
                </p>
                
                {selectedStrategy === 'manual_merge' ? (
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => handleFieldChange(conflict.field, 'client')}
                      className="p-3 border rounded-lg text-left hover:border-indigo-500"
                    >
                      <p className="text-xs text-gray-500 mb-1">Your version (Client)</p>
                      <p className="text-sm font-medium">{String(conflict.client_value)}</p>
                    </button>
                    <button
                      onClick={() => handleFieldChange(conflict.field, 'server')}
                      className="p-3 border rounded-lg text-left hover:border-indigo-500"
                    >
                      <p className="text-xs text-gray-500 mb-1">Server version</p>
                      <p className="text-sm font-medium">{String(conflict.server_value)}</p>
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white rounded border">
                      <p className="text-xs text-gray-500 mb-1">Your version</p>
                      <p className="text-sm">{String(conflict.client_value)}</p>
                    </div>
                    <div className="p-3 bg-white rounded border">
                      <p className="text-xs text-gray-500 mb-1">Server version</p>
                      <p className="text-sm">{String(conflict.server_value)}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={() => onResolve(selectedStrategy, selectedStrategy === 'manual_merge' ? mergedData : undefined)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Resolve Conflict
          </button>
        </div>
      </div>
    </div>
  )
}
