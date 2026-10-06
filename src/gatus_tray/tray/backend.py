import logging
import webbrowser
from abc import ABC, abstractmethod

from gatus_tray.models import EndpointStatus, OverallState

log = logging.getLogger(__name__)


class TrayBackend(ABC):
    @abstractmethod
    def set_state(self, state: OverallState): 
        ...
    
    def set_endpoints(self, endpoints: list[EndpointStatus]):
        pass

    def set_error(self, message: str):
        pass

    def show(self):
        pass

    def hide(self):
        pass

    def quit(self):
        pass


class HeadlessTray(TrayBackend):
    def set_state(self, state):
        self.state = state

    def set_endpoints(self, endpoints):
        self.endpoints = endpoints

    def set_error(self, message):
        self.error = message


class AyatanaTray(TrayBackend):
    """Small Ayatana AppIndicator implementation for Ubuntu GNOME."""

    _icons = {  # noqa: RUF012
        OverallState.UP: "emblem-ok",
        OverallState.DOWN: "dialog-error",
        OverallState.UNKNOWN: "dialog-warning",
        OverallState.DEGRADED: "dialog-warning",
    }

    def __init__(self, url: str, quit_callback):
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            gi.require_version("AyatanaAppIndicator3", "0.1")
            from gi.repository import AyatanaAppIndicator3, Gtk
        except (ImportError, ValueError) as exc:
            raise RuntimeError(f"Unable to load Ayatana AppIndicator: {exc}") from exc

        self._gtk = Gtk
        self._url = url
        self._quit_callback = quit_callback
        self._endpoints: list[EndpointStatus] = []
        self._error: str | None = None
        self._state = OverallState.UNKNOWN
        self._indicator = AyatanaAppIndicator3.Indicator.new(
            "gatus-tray",
            self._icons[self._state],
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
        self._rebuild_menu()

    def set_state(self, state: OverallState):
        self._state = state
        self._indicator.set_icon(self._icons[state])
        self._rebuild_menu()

    def set_endpoints(self, endpoints: list[EndpointStatus]):
        self._endpoints = endpoints
        self._error = None
        self._rebuild_menu()

    def set_error(self, message: str):
        self._error = message
        self._rebuild_menu()

    def _rebuild_menu(self):
        menu = self._gtk.Menu()
        status = self._gtk.MenuItem(label=f"Gatus: {self._state.value}")
        status.set_sensitive(False)
        menu.append(status)
        menu.append(self._gtk.SeparatorMenuItem())
        if self._error:
            error = self._gtk.MenuItem(label=f"Error: {self._error}")
            error.set_sensitive(False)
            menu.append(error)
        elif self._endpoints:
            for endpoint in self._endpoints:
                health = "UP" if endpoint.success else "DOWN"
                timing = (
                    f" — {endpoint.response_time_ms:.1f} ms"
                    if endpoint.response_time_ms is not None
                    else ""
                )
                icon_name = "emblem-ok" if endpoint.success else "dialog-error"
                icon = self._gtk.Image.new_from_icon_name(
                    icon_name, self._gtk.IconSize.MENU
                )
                item = self._gtk.ImageMenuItem(label=f"{endpoint.name}: {health}{timing}")
                item.set_image(icon)
                item.set_always_show_image(True)
                item.set_sensitive(False)
                menu.append(item)
        else:
            empty = self._gtk.MenuItem(label="No endpoint data")
            empty.set_sensitive(False)
            menu.append(empty)
        menu.append(self._gtk.SeparatorMenuItem())
        open_item = self._gtk.MenuItem(label="Open Gatus")
        open_item.connect("activate", lambda *_: webbrowser.open(self._url))
        menu.append(open_item)
        quit_item = self._gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda *_: self._quit_callback())
        menu.append(quit_item)
        menu.show_all()
        self._indicator.set_menu(menu)

    def quit(self):
        self._quit_callback()
