import { Menu, LogOut, User } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { useState, useRef, useEffect } from 'react'
import { NotificationCenter } from '../common'

interface HeaderProps {
  onMenuClick: () => void
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuthStore()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const getRoleDisplayName = (role: string) => {
    const roleMap: Record<string, string> = {
      STATE_ADMIN: 'State Admin',
      DISTRICT_ADMIN: 'District Admin',
      BLOCK_SUPERVISOR: 'Block Supervisor',
      AWW: 'Anganwadi Worker',
      SUPPLIER: 'Supplier',
      TRANSPORTER: 'Transporter',
    }
    return roleMap[role] || role
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 lg:px-6">
      <button
        onClick={onMenuClick}
        className="rounded-md p-2 text-gray-500 hover:bg-gray-100 lg:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="hidden lg:block">
        <h1 className="text-lg font-semibold text-gray-900">
          Anganwadi Supply Chain Management
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <NotificationCenter />

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 rounded-full p-1 hover:bg-gray-100"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-medium text-white">
              {user?.full_name?.charAt(0).toUpperCase() || <User className="h-4 w-4" />}
            </div>
            <div className="hidden text-left md:block">
              <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-xs text-gray-500">{user?.role && getRoleDisplayName(user.role)}</p>
            </div>
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-md border border-gray-200 bg-white py-1 shadow-lg">
              <div className="border-b border-gray-100 px-4 py-2 md:hidden">
                <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={() => {
                  setDropdownOpen(false)
                  logout()
                }}
                className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
