from datetime import datetime


def log(log_type: str, message: str):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_line = f'\n {timestamp} [{log_type}]: {message}'

    with open('files/log.txt', 'a') as f_handle:
        f_handle.write(log_line)
    pass
