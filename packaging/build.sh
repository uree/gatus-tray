#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
STAGING_DIR="$SCRIPT_DIR/root"
SERVICE_SOURCE="$SCRIPT_DIR/gatus-tray.service"
VERSION=$(
    python3 -c '
import tomllib
from pathlib import Path

with open(Path("pyproject.toml"), "rb") as f:
    print(tomllib.load(f)["project"]["version"])
'
)

rm -rf -- "$STAGING_DIR"
mkdir -p -- "$STAGING_DIR"

install -d -- "$STAGING_DIR/usr/lib/gatus-tray"
BUILD_VENV="$STAGING_DIR/usr/lib/gatus-tray/venv"

python3 -m venv --system-site-packages "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install "$REPO_ROOT"

# Verify the build venv can access Ubuntu's system PyGObject/GTK bindings
"$BUILD_VENV/bin/python" -c \
    'import gi; from gi.repository import Gtk; print("GTK/PyGObject OK")'

install -d -- "$STAGING_DIR/usr/bin"
cat > "$STAGING_DIR/usr/bin/gatus-tray" <<'EOF'
#!/usr/bin/env bash
exec /usr/lib/gatus-tray/venv/bin/python -m gatus_tray "$@"
EOF
chmod 0755 "$STAGING_DIR/usr/bin/gatus-tray"

install -D --mode=0644 \
    "$SERVICE_SOURCE" \
    "$STAGING_DIR/usr/lib/systemd/user/gatus-tray.service"

# Build the .deb file
fpm \
    --input-type dir \
    --output-type deb \
    --name gatus-tray \
    --version "$VERSION" \
    --architecture native \
    --description "Gatus tray monitor" \
    --depends "python3-gi" \
    --depends "gir1.2-gtk-3.0" \
    --depends "gir1.2-ayatanaappindicator3-0.1" \
    --depends "libayatana-appindicator3-1" \
    --depends "libnotify-bin" \
    --depends "gnome-shell-extension-appindicator" \
    -C "$STAGING_DIR" \
    .
