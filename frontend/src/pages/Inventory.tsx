import { useState, useEffect } from 'react'
import { Plus } from 'lucide-react'
import api from '../lib/api'
import { Card } from '../components/common/Card'
import Button from '../components/common/Button'
import Modal from '../components/common/Modal'

interface InventoryItem {
  id: number
  item_id: number
  item_name: string
  warehouse_id: number
  warehouse_name: string
  anganwadi_center_id: number
  center_name: string
  quantity: number
  min_threshold: number
  max_threshold: number
}

const InventoryPage: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [adjustModal, setAdjustModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [adjustData, setAdjustData] = useState({
    item_id: 0,
    warehouse_id: null as number | null,
    anganwadi_center_id: null as number | null,
    quantity: 0,
    adjustment_type: 'add',
    reason: ''
  })

  useEffect(() => {
    fetchInventory()
  }, [])

  const fetchInventory = async () => {
    try {
      setLoading(true)
      const response = await api.get('/supply-chain/inventory')
      setInventory(response.data.items || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAdjustInventory = async () => {
    try {
      await api.post('/supply-chain/inventory/adjust', adjustData)
      setAdjustModal(false)
      setAdjustData({
        item_id: 0,
        warehouse_id: null,
        anganwadi_center_id: null,
        quantity: 0,
        adjustment_type: 'add',
        reason: ''
      })
      fetchInventory()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const getStockStatus = (quantity: number, minThreshold: number, maxThreshold: number) => {
    if (quantity <= minThreshold) return { status: 'Low', color: 'text-red-600 bg-red-100' }
    if (quantity >= maxThreshold) return { status: 'High', color: 'text-green-600 bg-green-100' }
    return { status: 'Normal', color: 'text-blue-600 bg-blue-100' }
  }

  const filteredInventory = inventory.filter(item => 
    searchQuery === '' || item.item_name?.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <p className="text-gray-600">Manage stock levels</p>
        </div>
        <Button onClick={() => setAdjustModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Adjust Stock
        </Button>
      </div>

      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search inventory..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
      )}

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Warehouse</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Center</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => {
                const stockStatus = getStockStatus(item.quantity, item.min_threshold, item.max_threshold)
                return (
                  <tr key={item.id}>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.item_name || `Item ${item.item_id}`}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.warehouse_name || 'N/A'}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.center_name || 'N/A'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 font-medium">{item.quantity}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${stockStatus.color}`}>
                        {stockStatus.status}
                      </span>
                    </td>
                  </tr>
                )
              })}
              {filteredInventory.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No inventory items found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Modal isOpen={adjustModal} onClose={() => setAdjustModal(false)} title="Adjust Stock">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Item ID</label>
            <input
              type="number"
              value={adjustData.item_id}
              onChange={(e) => setAdjustData({ ...adjustData, item_id: parseInt(e.target.value) })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Quantity</label>
            <input
              type="number"
              value={adjustData.quantity}
              onChange={(e) => setAdjustData({ ...adjustData, quantity: parseFloat(e.target.value) })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Type</label>
            <select
              value={adjustData.adjustment_type}
              onChange={(e) => setAdjustData({ ...adjustData, adjustment_type: e.target.value })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="add">Add</option>
              <option value="subtract">Subtract</option>
              <option value="set">Set</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Reason</label>
            <input
              type="text"
              value={adjustData.reason}
              onChange={(e) => setAdjustData({ ...adjustData, reason: e.target.value })}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="secondary" onClick={() => setAdjustModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleAdjustInventory}>
            Save
          </Button>
        </div>
      </Modal>
    </div>
  )
}

export default InventoryPage
