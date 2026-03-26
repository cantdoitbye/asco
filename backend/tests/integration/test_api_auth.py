import pytest


class TestAuthRegister:
    def test_register_success(self, client, test_user):
        response = client.post("/api/v1/auth/register", json=test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["full_name"] == test_user["full_name"]
        assert data["role"] == test_user["role"]
        assert "id" in data
        assert data["is_active"] is True

    def test_register_duplicate_email(self, client, test_user):
        client.post("/api/v1/auth/register", json=test_user)
        response = client.post("/api/v1/auth/register", json=test_user)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Email already registered"


class TestAuthLogin:
    def test_login_success(self, client, test_user):
        client.post("/api/v1/auth/register", json=test_user)
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["email"] == test_user["email"]

    def test_login_invalid_credentials_wrong_password(self, client, test_user):
        client.post("/api/v1/auth/register", json=test_user)
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_invalid_credentials_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "anypassword"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"


class TestAuthMe:
    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "role" in data

    def test_get_current_user_without_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_get_current_user_with_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
