from pathlib import Path
from datetime import datetime
import re


class Logger:
    VERBOSE = False

    @staticmethod
    def _last_log_date(log_file):
        for line in reversed(log_file.read_text(encoding="utf-8").splitlines()):
            match = re.match(r"^\[([^]]+)\]", line)
            if match:
                return datetime.fromisoformat(match.group(1)).date()
        return None

    def __init__(self):
        self.dir = Path(__file__).resolve().parent / "logs"
        self.dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.dir / "current.txt"
        today = datetime.now().date()

        if self.log_file.exists():
            created_date = self._last_log_date(self.log_file)

            if created_date is not None and created_date != today:
                archived_file = self.dir / f"{created_date}.txt"

                if archived_file.exists():
                    archived_file = self.dir / f"{created_date}_{datetime.now():%H-%M-%S-%f}.txt"

                self.log_file.rename(archived_file)

        self.dmp = self.log_file.open("a", encoding="utf-8")

        if self.log_file.stat().st_size == 0:
            self.log("Created new log file")

        self.log("Initialised logger")

    def timestamp(self):
        if self.VERBOSE:
            return datetime.now().isoformat(sep=" ")
        else:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(self, message):
        self.dmp.write(f"[{self.timestamp()}] {message}\n")
        self.dmp.flush()

    def info(self, message):
        self.log(f"INFO: {message}")

    def error(self, message):
        self.log(f"ERROR: {message}")

    def debug(self, message):
        if self.VERBOSE:
            self.log(f"DEBUG: {message}")

    def close(self, message=None):
        if not self.dmp.closed:
            if message: self.log(f"Terminating logger with message: {message}")
            self.dmp.close()
