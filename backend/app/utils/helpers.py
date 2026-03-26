import uuid
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal


def generate_tracking_code() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"DEL-{timestamp}-{random_suffix}"


def generate_ticket_number() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"GRV-{timestamp}-{random_suffix}"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def calculate_trust_zone(score: Decimal) -> str:
    if score >= Decimal("4.0"):
        return "GREEN"
    elif score >= Decimal("3.0"):
        return "YELLOW"
    elif score >= Decimal("2.0"):
        return "ORANGE"
    else:
        return "RED"


def format_currency(amount: Decimal, currency: str = "INR") -> str:
    return f"₹{amount:,.2f}"


def format_date(date: datetime, format_str: str = "%d-%m-%Y") -> str:
    return date.strftime(format_str)


def format_datetime(dt: datetime, format_str: str = "%d-%m-%Y %H:%M") -> str:
    return dt.strftime(format_str)


def get_date_range(days: int = 30) -> tuple:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date
