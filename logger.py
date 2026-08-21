from pathlib import Path
from datetime import datetime

class Logger:
    VERBOSE = True

    def __init__(self):
        self.dir = Path("logs")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.dir / "log_current.txt"
        self.log_file.write_text(f"[{self.timestamp()}] Initialised logger")

    def timestamp(self):
        if self.VERBOSE:
            return datetime.now().isoformat(sep=" ")
        else:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(self, message):
        with self.log_file.open("a") as f:
            f.write(f"\n[{self.timestamp()}] {message}")

    def info(self, message):
        self.log(f"INFO: {message}")

    def error(self, message):
        self.log(f"ERROR: {message}")