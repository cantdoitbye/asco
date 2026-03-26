import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import RouteOptimization from './pages/RouteOptimization'
import SupplyChain from './pages/SupplyChain'
import Deliveries from './pages/Deliveries'
import Inventory from './pages/Inventory'
import DemandForecast from './pages/DemandForecast'
import Grievances from './pages/Grievances'
import TrustScores from './pages/TrustScores'
import Recommendations from './pages/Recommendations'
import Compliance from './pages/Compliance'
import StakeholderNetwork from './pages/StakeholderNetwork'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="route-optimization" element={<RouteOptimization />} />
          <Route path="supply-chain" element={<SupplyChain />} />
          <Route path="deliveries" element={<Deliveries />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="demand-forecast" element={<DemandForecast />} />
          <Route path="grievances" element={<Grievances />} />
          <Route path="trust-scores" element={<TrustScores />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="compliance" element={<Compliance />} />
          <Route path="network" element={<StakeholderNetwork />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
