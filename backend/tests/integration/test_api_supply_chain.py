import pytest
from datetime import datetime


class TestSupplyChainDeliveries:
    @pytest.mark.asyncio
    async def test_list_deliveries_with_auth(self, client, auth_headers):
        response = client.get("/api/v1/supply-chain/deliveries", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_deliveries_without_auth(self, client):
        response = client.get("/api/v1/supply-chain/deliveries")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_create_delivery_with_auth(self, client, auth_headers):
        delivery_data = {
            "warehouse_id": 1,
            "anganwadi_center_id": 1,
            "transport_fleet_id": 1,
            "scheduled_date": datetime.utcnow().isoformat(),
            "total_weight_kg": 100.5,
            "notes": "Test delivery"
        }
        response = client.post(
            "/api/v1/supply-chain/deliveries",
            json=delivery_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "tracking_code" in data
        assert data["warehouse_id"] == delivery_data["warehouse_id"]
        assert data["anganwadi_center_id"] == delivery_data["anganwadi_center_id"]
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_deliveries_with_status_filter(self, client, auth_headers):
        response = client.get(
            "/api/v1/supply-chain/deliveries?status=pending",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        for item in data["items"]:
            assert item["status"] == "pending"


class TestSupplyChainInventory:
    @pytest.mark.asyncio
    async def test_list_inventory_with_auth(self, client, auth_headers):
        response = client.get("/api/v1/supply-chain/inventory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_list_inventory_without_auth(self, client):
        response = client.get("/api/v1/supply-chain/inventory")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_list_inventory_with_warehouse_filter(self, client, auth_headers):
        response = client.get(
            "/api/v1/supply-chain/inventory?warehouse_id=1",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_inventory_with_low_stock_filter(self, client, auth_headers):
        response = client.get(
            "/api/v1/supply-chain/inventory?low_stock=true",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
