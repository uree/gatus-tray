# gatus-tray

A small Linux desktop tray monitor for Gatus. It polls Gatus' status API and reports endpoint health without talking to monitored websites directly.

## Supported environment

Ubuntu with GNOME and Python 3.12+. The indicator uses the StatusNotifier/AppIndicator protocol through Ayatana when the system bindings are installed. Vanilla GNOME may also require the AppIndicator/KStatusNotifierItem Support extension.

## Install system dependencies

```sh
sudo apt update
sudo apt install python3.12 python3.12-venv python3-gi gir1.2-gtk-3.0 \
  gir1.2-ayatanaappindicator3-0.1 libayatana-appindicator3-1 \
  libnotify-bin gnome-shell-extension-appindicator
```

Enable the extension in GNOME Extensions if it is not already enabled, then log out and in if necessary.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m gatus_tray
# or: gatus-tray
```

Configuration is read from `~/.config/gatus-tray/config.toml`; a default is used when it does not exist. Example:

```toml
backend = "gatus"
url = "http://localhost:8050"
poll_interval = 30
notifications_enabled = true
```

Run tests with `python -m pip install -e '.[test]' && python -m pytest`. Set `GATUS_TRAY_LOG_LEVEL=DEBUG` for diagnostics.

This is an initial proof of concept: settings UI, multiple configured instances, autostart installation, and a polished custom icon are not implemented. The indicator uses Ubuntu's Ayatana AppIndicator StatusNotifier integration; GNOME may require the AppIndicator/KStatusNotifierItem Support extension to display it in the top bar. Notifications use `notify-send`, supplied by `libnotify-bin`.


# Run as service

Put something like this in `~/.config/systemd/user/gatus-tray.service`.

[Unit]
Description=Gatus Tray Monitor
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=%h/path-to-gatus-tray/gatus-tray
ExecStart=%h/path-to-gatus-tray/gatus-tray/.venv/bin/python -m gatus_tray
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target

Then

```
systemctl --user daemon-reload
systemctl --user enable --now gatus-tray.service
```