import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from gatus_tray.backends.gatus import GatusClient
from gatus_tray.config import load_config
from gatus_tray.monitor import Monitor
from gatus_tray.notifications import Notifications
from gatus_tray.tray.backend import AyatanaTray

log = logging.getLogger(__name__)

class App:
    def __init__(self):
        c = load_config()
        self.notifications = Notifications(c.notifications_enabled)
        self._url = c.url
        self.tray = AyatanaTray(c.url, self.quit)
        self.monitor = Monitor(GatusClient(c.url), c.poll_interval, self._thread_update)
        self._stopping = False
        self._previous: dict[str, bool] = {}

    def _thread_update(self, state, endpoints, error):
        GLib.idle_add(self._update, state, endpoints, error)

    def _update(self, state, endpoints, error):
        self.tray.set_state(state)
        self.tray.set_endpoints(endpoints)
        if error:
            self.tray.set_error(error)
            self.notifications.notify_error(error)
            log.error("status unknown: %s", error)
        else:
            log.info("overall=%s endpoints=%d", state.value, len(endpoints))
        for endpoint in endpoints:
            old = self._previous.get(endpoint.key)
            if old is not None and old != endpoint.success:
                (
                    self.notifications.notify_recovered
                    if endpoint.success
                    else self.notifications.notify_down
                )(endpoint)
        self._previous = {endpoint.key: endpoint.success for endpoint in endpoints}

    def run(self):
        log.info("starting gatus-tray; connecting to configured Gatus instance")
        self.monitor.start()
        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.quit()

    def quit(self):
        if self._stopping:
            return
        self._stopping = True
        self.monitor.stop()
        Gtk.main_quit()
