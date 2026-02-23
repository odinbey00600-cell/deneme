import psutil


def system_stats() -> dict:
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'ram_percent': psutil.virtual_memory().percent
    }
