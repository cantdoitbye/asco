import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  Truck,
  BarChart3,
  AlertTriangle,
  Shield,
  Users,
  Lightbulb,
  X,
  Box,
  MapPin,
  TrendingUp,
} from 'lucide-react'
import clsx from 'clsx'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Supply Chain', href: '/supply-chain', icon: Package },
  { name: 'Deliveries', href: '/deliveries', icon: Truck },
  { name: 'Inventory', href: '/inventory', icon: Box },
  { name: 'Route Optimization', href: '/route-optimization', icon: MapPin },
  { name: 'Demand Forecast', href: '/demand-forecast', icon: TrendingUp },
  { name: 'Trust Scores', href: '/trust-scores', icon: Shield },
  { name: 'Grievances', href: '/grievances', icon: AlertTriangle },
  { name: 'Recommendations', href: '/recommendations', icon: Lightbulb },
  { name: 'Compliance', href: '/compliance', icon: BarChart3 },
  { name: 'Network', href: '/network', icon: Users },
]

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      <div
        className={clsx(
          'fixed inset-0 z-40 bg-gray-600/75 transition-opacity lg:hidden',
          open ? 'opacity-100' : 'pointer-events-none opacity-0'
        )}
        onClick={onClose}
      />

      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-gray-200 px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
              <Package className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900">Ooumph SHAKTI</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-gray-500 hover:bg-gray-100 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
            {navigation.map((item) => (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  onClick={onClose}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    )
                  }
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {item.name}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="border-t border-gray-200 p-4">
          <p className="text-xs text-gray-500">
            Anganwadi Supply Chain Management
          </p>
        </div>
      </aside>
    </>
  )
}
