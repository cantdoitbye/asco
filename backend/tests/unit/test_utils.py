import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
import os

from app.utils.helpers import (
    generate_tracking_code,
    generate_ticket_number,
    generate_uuid,
    calculate_trust_zone,
    format_currency,
    format_date,
    format_datetime,
    get_date_range,
)
from app.config import Settings, settings


class TestGenerateTrackingCode:
    def test_generate_tracking_code_returns_string(self):
        code = generate_tracking_code()
        assert isinstance(code, str)

    def test_generate_tracking_code_starts_with_del(self):
        code = generate_tracking_code()
        assert code.startswith("DEL-")

    def test_generate_tracking_code_format(self):
        code = generate_tracking_code()
        parts = code.split("-")
        assert len(parts) == 3
        assert parts[0] == "DEL"
        assert len(parts[1]) == 14
        assert len(parts[2]) == 6

    def test_generate_tracking_code_unique(self):
        code1 = generate_tracking_code()
        code2 = generate_tracking_code()
        assert code1 != code2

    def test_generate_tracking_code_timestamp_valid(self):
        code = generate_tracking_code()
        timestamp_part = code.split("-")[1]
        datetime.strptime(timestamp_part, "%Y%m%d%H%M%S")


class TestGenerateTicketNumber:
    def test_generate_ticket_number_returns_string(self):
        ticket = generate_ticket_number()
        assert isinstance(ticket, str)

    def test_generate_ticket_number_starts_with_grv(self):
        ticket = generate_ticket_number()
        assert ticket.startswith("GRV-")

    def test_generate_ticket_number_format(self):
        ticket = generate_ticket_number()
        parts = ticket.split("-")
        assert len(parts) == 3
        assert parts[0] == "GRV"
        assert len(parts[1]) == 14
        assert len(parts[2]) == 6

    def test_generate_ticket_number_unique(self):
        ticket1 = generate_ticket_number()
        ticket2 = generate_ticket_number()
        assert ticket1 != ticket2


class TestGenerateUuid:
    def test_generate_uuid_returns_string(self):
        uuid = generate_uuid()
        assert isinstance(uuid, str)

    def test_generate_uuid_format(self):
        uuid = generate_uuid()
        parts = uuid.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_generate_uuid_unique(self):
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2

    def test_generate_uuid_length(self):
        uuid = generate_uuid()
        assert len(uuid) == 36


class TestCalculateTrustZone:
    def test_calculate_trust_zone_green(self):
        assert calculate_trust_zone(Decimal("4.0")) == "GREEN"
        assert calculate_trust_zone(Decimal("4.5")) == "GREEN"
        assert calculate_trust_zone(Decimal("5.0")) == "GREEN"

    def test_calculate_trust_zone_yellow(self):
        assert calculate_trust_zone(Decimal("3.0")) == "YELLOW"
        assert calculate_trust_zone(Decimal("3.5")) == "YELLOW"
        assert calculate_trust_zone(Decimal("3.99")) == "YELLOW"

    def test_calculate_trust_zone_orange(self):
        assert calculate_trust_zone(Decimal("2.0")) == "ORANGE"
        assert calculate_trust_zone(Decimal("2.5")) == "ORANGE"
        assert calculate_trust_zone(Decimal("2.99")) == "ORANGE"

    def test_calculate_trust_zone_red(self):
        assert calculate_trust_zone(Decimal("0.0")) == "RED"
        assert calculate_trust_zone(Decimal("1.0")) == "RED"
        assert calculate_trust_zone(Decimal("1.99")) == "RED"

    def test_calculate_trust_zone_boundary_green(self):
        assert calculate_trust_zone(Decimal("4.0")) == "GREEN"
        assert calculate_trust_zone(Decimal("3.99")) == "YELLOW"

    def test_calculate_trust_zone_boundary_yellow(self):
        assert calculate_trust_zone(Decimal("3.0")) == "YELLOW"
        assert calculate_trust_zone(Decimal("2.99")) == "ORANGE"

    def test_calculate_trust_zone_boundary_orange(self):
        assert calculate_trust_zone(Decimal("2.0")) == "ORANGE"
        assert calculate_trust_zone(Decimal("1.99")) == "RED"


class TestFormatCurrency:
    def test_format_currency_basic(self):
        result = format_currency(Decimal("1000"))
        assert result == "₹1,000.00"

    def test_format_currency_with_decimals(self):
        result = format_currency(Decimal("1234.56"))
        assert result == "₹1,234.56"

    def test_format_currency_zero(self):
        result = format_currency(Decimal("0"))
        assert result == "₹0.00"

    def test_format_currency_large_number(self):
        result = format_currency(Decimal("1000000"))
        assert result == "₹1,000,000.00"

    def test_format_currency_small_number(self):
        result = format_currency(Decimal("0.01"))
        assert result == "₹0.01"


class TestFormatDate:
    def test_format_date_default_format(self):
        date = datetime(2024, 1, 15)
        result = format_date(date)
        assert result == "15-01-2024"

    def test_format_date_custom_format(self):
        date = datetime(2024, 1, 15)
        result = format_date(date, "%Y-%m-%d")
        assert result == "2024-01-15"

    def test_format_date_with_month_name(self):
        date = datetime(2024, 1, 15)
        result = format_date(date, "%d %B %Y")
        assert result == "15 January 2024"

    def test_format_date_different_date(self):
        date = datetime(2024, 12, 25)
        result = format_date(date)
        assert result == "25-12-2024"


class TestFormatDatetime:
    def test_format_datetime_default_format(self):
        dt = datetime(2024, 1, 15, 14, 30)
        result = format_datetime(dt)
        assert result == "15-01-2024 14:30"

    def test_format_datetime_custom_format(self):
        dt = datetime(2024, 1, 15, 14, 30)
        result = format_datetime(dt, "%Y-%m-%d %H:%M:%S")
        assert result == "2024-01-15 14:30:00"

    def test_format_datetime_with_seconds(self):
        dt = datetime(2024, 6, 20, 9, 15, 45)
        result = format_datetime(dt, "%d-%m-%Y %H:%M:%S")
        assert result == "20-06-2024 09:15:45"


class TestGetDateRange:
    def test_get_date_range_default_30_days(self):
        start_date, end_date = get_date_range()
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        delta = (end_date - start_date).days
        assert delta == 30

    def test_get_date_range_custom_days(self):
        start_date, end_date = get_date_range(days=7)
        delta = (end_date - start_date).days
        assert delta == 7

    def test_get_date_range_one_day(self):
        start_date, end_date = get_date_range(days=1)
        delta = (end_date - start_date).days
        assert delta == 1

    def test_get_date_range_zero_days(self):
        start_date, end_date = get_date_range(days=0)
        assert start_date == end_date

    def test_get_date_range_end_date_is_now(self):
        start_date, end_date = get_date_range()
        now = datetime.now()
        diff = abs((end_date - now).total_seconds())
        assert diff < 1


class TestConfigLoading:
    def test_settings_default_project_name(self):
        test_settings = Settings()
        assert test_settings.PROJECT_NAME == "Ooumph SHAKTI API"

    def test_settings_default_version(self):
        test_settings = Settings()
        assert test_settings.VERSION == "1.0.0"

    def test_settings_default_api_v1_str(self):
        test_settings = Settings()
        assert test_settings.API_V1_STR == "/api/v1"

    def test_settings_default_database_url(self):
        test_settings = Settings()
        assert "postgresql" in test_settings.DATABASE_URL

    def test_settings_default_jwt_algorithm(self):
        test_settings = Settings()
        assert test_settings.JWT_ALGORITHM == "HS256"

    def test_settings_default_jwt_expiration_hours(self):
        test_settings = Settings()
        assert test_settings.JWT_EXPIRATION_HOURS == 24

    def test_settings_jwt_secret_default(self):
        test_settings = Settings()
        assert test_settings.JWT_SECRET == "your-super-secret-key-change-in-production"

    def test_settings_redis_url_default(self):
        test_settings = Settings()
        assert test_settings.REDIS_URL == "redis://localhost:6379"

    def test_settings_cors_origins_default(self):
        test_settings = Settings()
        assert "http://localhost:3000" in test_settings.CORS_ORIGINS
        assert "http://localhost:5173" in test_settings.CORS_ORIGINS

    def test_settings_openai_api_key_default(self):
        test_settings = Settings()
        assert test_settings.OPENAI_API_KEY is None

    def test_global_settings_instance(self):
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_settings_env_file_config(self):
        test_settings = Settings()
        assert hasattr(test_settings, "Config")

    @patch.dict(os.environ, {"JWT_SECRET": "test-secret-key"})
    def test_settings_jwt_secret_from_env(self):
        test_settings = Settings()
        assert test_settings.JWT_SECRET == "test-secret-key"

    @patch.dict(os.environ, {"JWT_EXPIRATION_HOURS": "48"})
    def test_settings_jwt_expiration_from_env(self):
        test_settings = Settings()
        assert test_settings.JWT_EXPIRATION_HOURS == 48

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost:5432/testdb"})
    def test_settings_database_url_from_env(self):
        test_settings = Settings()
        assert test_settings.DATABASE_URL == "postgresql://test:test@localhost:5432/testdb"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_settings_openai_api_key_from_env(self):
        test_settings = Settings()
        assert test_settings.OPENAI_API_KEY == "sk-test-key"


class TestHelperFunctionsIntegration:
    def test_tracking_code_and_ticket_are_different(self):
        tracking = generate_tracking_code()
        ticket = generate_ticket_number()
        assert tracking != ticket
        assert tracking.startswith("DEL-")
        assert ticket.startswith("GRV-")

    def test_format_functions_work_together(self):
        now = datetime.now()
        date_str = format_date(now)
        datetime_str = format_datetime(now)
        assert len(date_str) == 10
        assert len(datetime_str) >= 16

    def test_trust_zone_with_calculated_score(self):
        scores = [
            (Decimal("4.5"), "GREEN"),
            (Decimal("3.5"), "YELLOW"),
            (Decimal("2.5"), "ORANGE"),
            (Decimal("1.5"), "RED"),
        ]
        for score, expected_zone in scores:
            zone = calculate_trust_zone(score)
            assert zone == expected_zone

    def test_date_range_with_helpers(self):
        start_date, end_date = get_date_range(days=30)
        start_str = format_date(start_date)
        end_str = format_date(end_date)
        assert len(start_str) == 10
        assert len(end_str) == 10
