#!/bin/bash

# 🖥️ Desktop Icon Creator Script
# Based on successful ForgedKismet implementation
# Usage: ./create-desktop-icon.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🖥️ Desktop Icon Creator${NC}"
echo "=================================="

# Function to prompt for input with default
prompt_input() {
    local prompt="$1"
    local default="$2"
    local result
    
    if [[ -n "$default" ]]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

# Function to validate file exists
validate_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ Error: File not found: $file${NC}"
        return 1
    fi
    return 0
}

# Function to validate directory exists
validate_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}❌ Error: Directory not found: $dir${NC}"
        return 1
    fi
    return 0
}

# Collect information
echo -e "${YELLOW}📝 Application Information${NC}"
APP_NAME=$(prompt_input "Application Name" "MyApp")
APP_DESCRIPTION=$(prompt_input "Application Description" "My Local Application")

echo -e "\n${YELLOW}📁 File Paths${NC}"
APP_DIR=$(prompt_input "Application Directory" "$(pwd)")

# Validate app directory
if ! validate_dir "$APP_DIR"; then
    exit 1
fi

# Look for common executable patterns
echo -e "\n${BLUE}🔍 Looking for executables in $APP_DIR...${NC}"
EXECUTABLES=($(find "$APP_DIR" -maxdepth 2 -type f -executable 2>/dev/null | head -5))

if [[ ${#EXECUTABLES[@]} -gt 0 ]]; then
    echo "Found executables:"
    for i in "${!EXECUTABLES[@]}"; do
        echo "  $((i+1)). ${EXECUTABLES[$i]}"
    done
    
    EXEC_CHOICE=$(prompt_input "Choose executable number or enter custom path" "1")
    
    if [[ "$EXEC_CHOICE" =~ ^[0-9]+$ ]] && [[ "$EXEC_CHOICE" -le "${#EXECUTABLES[@]}" ]]; then
        APP_EXECUTABLE="${EXECUTABLES[$((EXEC_CHOICE-1))]}"
    else
        APP_EXECUTABLE="$EXEC_CHOICE"
    fi
else
    APP_EXECUTABLE=$(prompt_input "Executable path" "$APP_DIR/app")
fi

# Validate executable
if ! validate_file "$APP_EXECUTABLE"; then
    echo -e "${YELLOW}⚠️ Warning: Executable not found, but continuing...${NC}"
fi

# Look for icon files
echo -e "\n${BLUE}🔍 Looking for icon files in $APP_DIR...${NC}"
ICONS=($(find "$APP_DIR" -maxdepth 2 -name "*.png" -o -name "*.svg" -o -name "*.ico" 2>/dev/null | head -5))

if [[ ${#ICONS[@]} -gt 0 ]]; then
    echo "Found icons:"
    for i in "${!ICONS[@]}"; do
        echo "  $((i+1)). ${ICONS[$i]}"
    done
    
    ICON_CHOICE=$(prompt_input "Choose icon number or enter custom path" "1")
    
    if [[ "$ICON_CHOICE" =~ ^[0-9]+$ ]] && [[ "$ICON_CHOICE" -le "${#ICONS[@]}" ]]; then
        APP_ICON="${ICONS[$((ICON_CHOICE-1))]}"
    else
        APP_ICON="$ICON_CHOICE"
    fi
else
    APP_ICON=$(prompt_input "Icon path (.png recommended)" "$APP_DIR/icon.png")
fi

# Validate icon
if ! validate_file "$APP_ICON"; then
    echo -e "${YELLOW}⚠️ Warning: Icon not found, but continuing...${NC}"
fi

echo -e "\n${YELLOW}⚙️ Configuration Options${NC}"
CATEGORIES=$(prompt_input "Categories (semicolon-separated)" "Development;Utility;")
KEYWORDS=$(prompt_input "Keywords (semicolon-separated)" "app;utility;development;")
TERMINAL=$(prompt_input "Requires terminal? (true/false)" "false")

# Generate desktop file name
DESKTOP_FILE="${APP_NAME// /}.desktop"

echo -e "\n${BLUE}📄 Creating desktop file: $DESKTOP_FILE${NC}"

# Create desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=$APP_DESCRIPTION
Exec=$APP_EXECUTABLE
Icon=$APP_ICON
Terminal=$TERMINAL
Categories=$CATEGORIES
Keywords=$KEYWORDS
StartupNotify=true
StartupWMClass=${APP_NAME,,}
EOF

# Make executable
chmod +x "$DESKTOP_FILE"

echo -e "${GREEN}✅ Desktop file created: $DESKTOP_FILE${NC}"

# Show preview
echo -e "\n${BLUE}📋 Desktop File Preview:${NC}"
echo "=================================="
cat "$DESKTOP_FILE"
echo "=================================="

# Ask about deployment
echo -e "\n${YELLOW}🚀 Deployment Options${NC}"
echo "1. Copy to Desktop only"
echo "2. Copy to Desktop and Applications menu"
echo "3. Just create file (no deployment)"

DEPLOY_CHOICE=$(prompt_input "Choose deployment option" "1")

case "$DEPLOY_CHOICE" in
    1)
        cp "$DESKTOP_FILE" ~/Desktop/
        chmod +x ~/Desktop/"$DESKTOP_FILE"
        echo -e "${GREEN}✅ Copied to Desktop${NC}"
        ;;
    2)
        cp "$DESKTOP_FILE" ~/Desktop/
        chmod +x ~/Desktop/"$DESKTOP_FILE"
        
        if sudo cp "$DESKTOP_FILE" /usr/share/applications/ 2>/dev/null; then
            sudo update-desktop-database 2>/dev/null
            echo -e "${GREEN}✅ Copied to Desktop and Applications menu${NC}"
        else
            echo -e "${YELLOW}⚠️ Could not copy to system applications (no sudo access)${NC}"
            echo -e "${GREEN}✅ Copied to Desktop only${NC}"
        fi
        ;;
    3)
        echo -e "${GREEN}✅ Desktop file created only${NC}"
        ;;
    *)
        echo -e "${YELLOW}⚠️ Invalid choice, desktop file created only${NC}"
        ;;
esac

# Validation
echo -e "\n${BLUE}🔍 Validation${NC}"

if [[ -f "$APP_EXECUTABLE" ]]; then
    echo -e "${GREEN}✅ Executable exists${NC}"
else
    echo -e "${RED}❌ Executable not found${NC}"
fi

if [[ -f "$APP_ICON" ]]; then
    echo -e "${GREEN}✅ Icon exists${NC}"
else
    echo -e "${RED}❌ Icon not found${NC}"
fi

if command -v desktop-file-validate &> /dev/null; then
    if desktop-file-validate "$DESKTOP_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ Desktop file syntax valid${NC}"
    else
        echo -e "${YELLOW}⚠️ Desktop file syntax warnings (but should work)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ desktop-file-validate not available${NC}"
fi

echo -e "\n${GREEN}🎉 Desktop icon creation complete!${NC}"
echo -e "${BLUE}📁 Files created:${NC}"
echo "  - $DESKTOP_FILE"
if [[ "$DEPLOY_CHOICE" == "1" || "$DEPLOY_CHOICE" == "2" ]]; then
    echo "  - ~/Desktop/$DESKTOP_FILE"
fi
if [[ "$DEPLOY_CHOICE" == "2" ]]; then
    echo "  - /usr/share/applications/$DESKTOP_FILE"
fi

echo -e "\n${BLUE}🔧 To modify later, edit: $DESKTOP_FILE${NC}"
echo -e "${BLUE}📖 For more info, see: DESKTOP_ICON_CREATION_GUIDE.md${NC}"
