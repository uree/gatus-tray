import logging
import shutil
import subprocess

log = logging.getLogger(__name__)

class Notifications:
    def __init__(self, enabled=True):
        self.enabled, self.available = enabled, shutil.which("notify-send")

    def _send(self, title, message):
        if self.enabled and self.available:
            subprocess.Popen(
                [self.available, title, message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def notify_down(self, endpoint):
        self._send("Gatus endpoint down", endpoint.name)

    def notify_recovered(self, endpoint):
        self._send("Gatus endpoint recovered", endpoint.name)

    def notify_error(self, message):
        self._send("Gatus monitor error", message)
