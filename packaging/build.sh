#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
STAGING_DIR="$SCRIPT_DIR/root"
SERVICE_SOURCE="$SCRIPT_DIR/gatus-tray.service"

rm -rf -- "$STAGING_DIR"
mkdir -p -- "$STAGING_DIR"

install -d -- "$STAGING_DIR/usr/lib/gatus-tray"
BUILD_VENV="$STAGING_DIR/usr/lib/gatus-tray/venv"

python3 -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install "$REPO_ROOT"

install -d -- "$STAGING_DIR/usr/bin"
cat > "$STAGING_DIR/usr/bin/gatus-tray" <<'EOF'
#!/usr/bin/env bash
exec /usr/lib/gatus-tray/venv/bin/python -m gatus_tray "$@"
EOF
chmod 0755 "$STAGING_DIR/usr/bin/gatus-tray"

install -D --mode=0644 \
    "$SERVICE_SOURCE" \
    "$STAGING_DIR/usr/lib/systemd/user/gatus-tray.service"

# TODO: Replace this placeholder with the eventual FPM command and Debian metadata.
# fpm ... --root "$STAGING_DIR" ...
