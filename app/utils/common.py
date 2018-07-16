from datetime import datetime


def validate_date(dt, fmt):
    try:
        datetime.strptime(dt, fmt)
        return True
    except Exception as e:
        return False