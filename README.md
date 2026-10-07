# gatus-tray

A small Linux desktop tray monitor for Gatus. Displays which sites are up/down in the tray. Also sends notifications if any of them are unavailable.

Tested on ubuntu with GNOME and Python 3.12+. The indicator uses the StatusNotifier/AppIndicator protocol through Ayatana when the system bindings are installed. Vanilla GNOME may also require the AppIndicator/KStatusNotifierItem Support extension.

**Disclaimer**: This app was vibe coded in a couple of hours with Codex Luna Light.

## Install and configure Gatus

```
docker run -d \
  -p 8050:8080 \
  --mount type=bind,source="$(pwd)"/config.yaml,target=/config/config.yaml \
  --name gatus \
  ghcr.io/twin/gatus:stable
```

## Configuration (for manual and package)

Configuration is read from `~/.config/gatus-tray/config.toml`. A default is used when it does not exist:

```toml
backend = "gatus"
url = "http://localhost:8050"
poll_interval = 30
notifications_enabled = true
```

## Install deb package

Download `.deb` file from releases & run `sudo apt install ./package.deb`. Boink.

## Manual install 

Install system dependencies.

```sh
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 \
  gir1.2-ayatanaappindicator3-0.1 libayatana-appindicator3-1 \
  libnotify-bin gnome-shell-extension-appindicator
```

Set up venv and run.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m gatus_tray
```

Run tests with `python -m pip install -e '.[test]' && python -m pytest`. Set `GATUS_TRAY_LOG_LEVEL=DEBUG` for diagnostics.


Set up systemd. 

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

