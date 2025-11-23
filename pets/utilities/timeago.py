from datetime import datetime, timezone


def timeago(value):
        # Accept datetime or ISO string
        if isinstance(value, str):
            try:
                # Remove trailing Z if present
                value_dt = datetime.fromisoformat(value.replace('Z', ''))
            except ValueError:
                return value
        else:
            value_dt = value
        if not isinstance(value_dt, datetime):
            return str(value)
        # Normalize to naive UTC for diff
        if value_dt.tzinfo is not None:
            value_dt = value_dt.astimezone(timezone.utc).replace(tzinfo=None)
        now = datetime.utcnow()
        diff = now - value_dt
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Just now"
        minutes = seconds / 60
        if minutes < 60:
            return f"{int(minutes)}m"
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)}h"
        days = hours / 24
        if days < 7:
            return f"{int(days)}d"
        return value_dt.strftime("%d/%m/%y")