import os
import datetime
import threading


class Logger: 
    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls):
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):    
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        self._write_lock = threading.Lock()
        now = datetime.datetime.now()
        date_hour_string = now.strftime("%Y-%m-%d_%H-%M")
        self.file_name =os.path.join(log_dir, f"{date_hour_string}.log")

        with open(self.file_name, 'a') as f:
            f.write(f"Log started at {now}\n")

    def log(self, msg):
        now = datetime.datetime.now()
        time_string = now.strftime("%H:%M:%S")
        log_entry = f"{time_string} - {msg}\n"

        with self._write_lock:
            with open(self.file_name, 'a') as f:
                f.write(log_entry)

