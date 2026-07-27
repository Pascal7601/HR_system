from datetime import date

def is_valid_date_range(start_date: date, end_date: date) -> bool:
    """Check if the start_date is before or equal to the end_date."""
    return start_date is not None and end_date is not None and start_date <= end_date

def is_positive_number(value) -> bool:
    """Check if the given value is a positive number."""
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False