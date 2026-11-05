from datetime import date, datetime


def format_date(value):
    """Transforme '2026-11-02' (ou une date) en '02/11/2026'."""
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(value)