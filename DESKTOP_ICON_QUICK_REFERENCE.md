# 🚀 Desktop Icon Quick Reference

## TL;DR - Fast Implementation

### 1. Automated Script (Recommended)
```bash
./create-desktop-icon.sh
# Follow the interactive prompts
```

### 2. Manual Template
```bash
# Replace YOUR_* with actual values
cat > YourApp.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=YOUR_APP_NAME
Comment=YOUR_APP_DESCRIPTION
Exec=YOUR_FULL_PATH_TO_EXECUTABLE
Icon=YOUR_FULL_PATH_TO_ICON.png
Terminal=false
Categories=Development;Utility;
Keywords=app;utility;
StartupNotify=true
EOF

chmod +x YourApp.desktop
cp YourApp.desktop ~/Desktop/
```

## 📋 Essential Fields

| Field | Required | Example |
|-------|----------|---------|
| `Name` | ✅ | `MyApp` |
| `Exec` | ✅ | `/home/user/myapp/run.sh` |
| `Icon` | ✅ | `/home/user/myapp/icon.png` |
| `Type` | ✅ | `Application` |
| `Comment` | 📝 | `My awesome application` |
| `Categories` | 📝 | `Development;Network;` |
| `Terminal` | 📝 | `false` (GUI) or `true` (CLI) |

## 🎯 Common Categories

- **Development**: `Development;Programming;IDE;`
- **Network/Security**: `Network;Security;Monitoring;`
- **Multimedia**: `AudioVideo;Audio;Video;`
- **System Tools**: `System;Utility;`
- **Games**: `Game;`

## ⚡ One-Liner Creator

```bash
# Quick desktop icon creator
create_icon() {
    local name="$1" desc="$2" exec="$3" icon="$4"
    cat > "${name}.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${name}
Comment=${desc}
Exec=${exec}
Icon=${icon}
Terminal=false
Categories=Utility;
StartupNotify=true
EOF
    chmod +x "${name}.desktop"
    cp "${name}.desktop" ~/Desktop/
    echo "✅ Created: ${name}.desktop"
}

# Usage:
# create_icon "MyApp" "My Application" "/path/to/app" "/path/to/icon.png"
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Icon not showing | Use absolute paths, check file exists |
| App won't launch | Verify executable path and permissions |
| Not in menu | Check Categories field, run `update-desktop-database` |

## 📁 File Locations

- **User Desktop**: `~/Desktop/YourApp.desktop`
- **User Applications**: `~/.local/share/applications/YourApp.desktop`
- **System Applications**: `/usr/share/applications/YourApp.desktop`

## ✅ Validation

```bash
# Test desktop file
desktop-file-validate YourApp.desktop

# Test executable
/path/to/your/executable --version

# Check icon
file /path/to/your/icon.png
```

---
**For complete guide see: `DESKTOP_ICON_CREATION_GUIDE.md`**
