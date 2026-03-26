import pytest


class TestDashboardStats:
    @pytest.mark.asyncio
    async def test_get_dashboard_stats_with_auth(self, client, auth_headers):
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_anganwadi_centers" in data
        assert "total_beneficiaries" in data
        assert "total_deliveries" in data
        assert "pending_deliveries" in data
        assert "active_grievances" in data
        assert "avg_trust_score" in data
        assert "low_stock_alerts" in data
        assert "upcoming_scheduled_deliveries" in data
        assert isinstance(data["total_anganwadi_centers"], int)
        assert isinstance(data["total_beneficiaries"], int)
        assert isinstance(data["total_deliveries"], int)
        assert isinstance(data["pending_deliveries"], int)
        assert isinstance(data["active_grievances"], int)
        assert isinstance(data["low_stock_alerts"], int)
        assert isinstance(data["upcoming_scheduled_deliveries"], int)

    def test_get_dashboard_stats_without_auth(self, client):
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_dashboard_stats_returns_expected_structure(self, client, auth_headers):
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        expected_keys = [
            "total_anganwadi_centers",
            "total_beneficiaries",
            "total_deliveries",
            "pending_deliveries",
            "active_grievances",
            "avg_trust_score",
            "low_stock_alerts",
            "upcoming_scheduled_deliveries"
        ]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"
