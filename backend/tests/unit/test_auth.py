import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)
from app.config import settings


class TestPasswordHashing:
    def test_get_password_hash_returns_string(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert isinstance(hashed, str)
        assert hashed != password

    def test_get_password_hash_creates_different_hashes(self):
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_password_with_correct_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        password = "testpassword123"
        wrong_password = "wrongpassword456"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_empty_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False

    def test_verify_password_with_none_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        with pytest.raises(Exception):
            verify_password(None, hashed)


class TestJWTTokenCreation:
    def test_create_access_token_returns_string(self):
        data = {"sub": "1", "email": "test@test.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiration(self):
        data = {"sub": "1", "email": "test@test.com"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)
        assert isinstance(token, str)

    def test_create_access_token_with_default_expiration(self):
        data = {"sub": "1", "email": "test@test.com"}
        token = create_access_token(data)
        assert isinstance(token, str)

    def test_create_access_token_contains_data(self):
        data = {"sub": "123", "email": "user@example.com", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "123"
        assert decoded.get("email") == "user@example.com"
        assert decoded.get("role") == "admin"

    def test_create_access_token_with_empty_data(self):
        data = {}
        token = create_access_token(data)
        assert isinstance(token, str)
        decoded = decode_token(token)
        assert decoded is not None
        assert "exp" in decoded


class TestJWTTokenVerification:
    def test_decode_token_with_valid_token(self):
        data = {"sub": "1", "email": "test@test.com"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "1"
        assert decoded.get("email") == "test@test.com"

    def test_decode_token_with_invalid_token(self):
        invalid_token = "invalid.token.here"
        decoded = decode_token(invalid_token)
        assert decoded is None

    def test_decode_token_with_empty_token(self):
        decoded = decode_token("")
        assert decoded is None

    def test_decode_token_with_none_token(self):
        decoded = decode_token(None)
        assert decoded is None

    def test_decode_token_with_malformed_token(self):
        malformed_token = "not-a-valid-jwt"
        decoded = decode_token(malformed_token)
        assert decoded is None


class TestTokenExpiration:
    def test_token_contains_expiration(self):
        data = {"sub": "1", "email": "test@test.com"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert "exp" in decoded

    def test_token_with_custom_expiration(self):
        data = {"sub": "1", "email": "test@test.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        decoded = decode_token(token)
        assert decoded is not None
        assert "exp" in decoded

    def test_token_with_zero_expiration(self):
        data = {"sub": "1", "email": "test@test.com"}
        expires_delta = timedelta(seconds=0)
        token = create_access_token(data, expires_delta)
        decoded = decode_token(token)
        assert decoded is not None

    def test_token_expiration_time_is_correct(self):
        data = {"sub": "1", "email": "test@test.com"}
        expires_delta = timedelta(hours=2)
        before_creation = datetime.utcnow()
        token = create_access_token(data, expires_delta)
        after_creation = datetime.utcnow()
        decoded = decode_token(token)
        assert decoded is not None
        exp_timestamp = decoded.get("exp")
        expected_min = (before_creation + expires_delta).timestamp()
        expected_max = (after_creation + expires_delta).timestamp()
        assert exp_timestamp >= expected_min
        assert exp_timestamp <= expected_max


class TestPasswordAndTokenIntegration:
    def test_password_hash_and_token_workflow(self):
        password = "securepassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        user_data = {"sub": "42", "email": "user@test.com"}
        token = create_access_token(user_data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "42"

    def test_multiple_users_passwords_and_tokens(self):
        users = [
            {"id": "1", "email": "user1@test.com", "password": "pass1"},
            {"id": "2", "email": "user2@test.com", "password": "pass2"},
            {"id": "3", "email": "user3@test.com", "password": "pass3"},
        ]
        for user in users:
            hashed = get_password_hash(user["password"])
            assert verify_password(user["password"], hashed) is True
            token = create_access_token({"sub": user["id"], "email": user["email"]})
            decoded = decode_token(token)
            assert decoded is not None
            assert decoded.get("sub") == user["id"]
