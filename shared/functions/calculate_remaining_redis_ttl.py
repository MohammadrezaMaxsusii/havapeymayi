from datetime import datetime, timedelta

def seconds_until_midnight():
    """Calculate the number of seconds remaining until midnight (00:00) of the next day."""
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((midnight - now).total_seconds())

