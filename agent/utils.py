from datetime import datetime


def get_current_datetime():
    now = datetime.now().astimezone()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z (%z)")
