#!/bin/sh
# Автозапуск панели, бота и туннеля при входе в macOS (launchd).
# Установить:  ./deploy/install_autostart.sh
# Удалить:     ./deploy/install_autostart.sh --remove
# Лог:         ~/Library/Logs/nurlight.log
set -e
LABEL=rest.moji.nurlight
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true

if [ "$1" = "--remove" ]; then
    rm -f "$PLIST"
    echo "Автозапуск отключён"
    exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$LABEL</string>
    <key>ProgramArguments</key>
    <array><string>/bin/sh</string><string>$REPO/deploy/start_public.sh</string></array>
    <key>WorkingDirectory</key><string>$REPO</string>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>ThrottleInterval</key><integer>30</integer>
    <key>StandardOutPath</key><string>$HOME/Library/Logs/nurlight.log</string>
    <key>StandardErrorPath</key><string>$HOME/Library/Logs/nurlight.log</string>
</dict>
</plist>
PLIST

launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Автозапуск включён. Лог: ~/Library/Logs/nurlight.log"
