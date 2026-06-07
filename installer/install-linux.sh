#!/usr/bin/env bash
# raceGPS Linux Installer
# Usage: ./install.sh [--prefix /opt/racegps] [--user]
# Supports: Ubuntu 22.04+, Fedora 38+, Arch Linux

set -euo pipefail

PRODUCT_NAME="raceGPS"
PRODUCT_VERSION="0.2.0"
PUBLISHER="LumenHelix Solutions"
REPO_URL="https://github.com/lumenhelixsolutions/raceGPS"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Defaults
PREFIX="/opt/${PRODUCT_NAME,,}"
USER_INSTALL=false
SKIP_PREFLIGHT=false
SKIP_DEPS=false

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix) PREFIX="$2"; shift 2 ;;
        --user) PREFIX="$HOME/.local/share/${PRODUCT_NAME,,}"; USER_INSTALL=true; shift ;;
        --skip-preflight) SKIP_PREFLIGHT=true; shift ;;
        --skip-deps) SKIP_DEPS=true; shift ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "  --prefix PATH    Install to custom path (default: /opt/racegps)"
            echo "  --user           Install to ~/.local/share/racegps"
            echo "  --skip-preflight Skip hardware checks"
            echo "  --skip-deps      Skip dependency installation"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Logging
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
ok() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================
# HEADER
# ============================================================
echo ""
echo "========================================"
echo "  ${PRODUCT_NAME} ${PRODUCT_VERSION}"
echo "  Linux Installer"
echo "========================================"
echo ""

# ============================================================
# PREFLIGHT CHECKS
# ============================================================
if [[ "$SKIP_PREFLIGHT" == "false" ]]; then
    log "Running pre-flight checks..."

    # Architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" ]]; then
        err "Unsupported architecture: $ARCH. x86_64 required."
        exit 1
    fi
    ok "Architecture: $ARCH"

    # RAM
    RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    RAM_MB=$((RAM_KB / 1024))
    if [[ $RAM_MB -lt 8192 ]]; then
        warn "RAM: ${RAM_MB} MB (8 GB recommended)"
    else
        ok "RAM: ${RAM_MB} MB"
    fi

    # Disk space
    DISK_KB=$(df -k "$PREFIX" 2>/dev/null | tail -1 | awk '{print $4}')
    if [[ -z "$DISK_KB" ]]; then
        DISK_KB=$(df -k /tmp | tail -1 | awk '{print $4}')
    fi
    DISK_MB=$((DISK_KB / 1024))
    if [[ $DISK_MB -lt 5120 ]]; then
        err "Disk space: ${DISK_MB} MB free (5 GB required)"
        exit 1
    fi
    ok "Disk space: ${DISK_MB} MB available"

    # OS Version
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        log "OS: $NAME $VERSION_ID"
        case "$ID" in
            ubuntu|debian|pop)
                if [[ "${VERSION_ID%%.*}" -lt 22 ]]; then
                    warn "Ubuntu/Debian 22.04+ recommended"
                fi
                ;;
            fedora|rhel|centos)
                if [[ "${VERSION_ID%%.*}" -lt 38 ]]; then
                    warn "Fedora 38+ recommended"
                fi
                ;;
            arch|manjaro)
                ok "Arch-based distribution detected"
                ;;
            *) warn "Untested distribution: $ID"; ;;
        esac
    fi

    # GPU / Vulkan
    if command -v vulkaninfo &>/dev/null; then
        VULKAN_VER=$(vulkaninfo --summary 2>/dev/null | grep "Vulkan Instance Version" | awk '{print $4}' || echo "unknown")
        ok "Vulkan runtime: $VULKAN_VER"
    else
        warn "Vulkan runtime not detected. Will install vulkan-tools if possible."
    fi

    # CPU cores
    CORES=$(nproc)
    if [[ $CORES -lt 4 ]]; then
        warn "CPU cores: $CORES (4+ recommended)"
    else
        ok "CPU cores: $CORES"
    fi

    echo ""
fi

# ============================================================
# DEPENDENCY INSTALLATION
# ============================================================
if [[ "$SKIP_DEPS" == "false" ]]; then
    log "Checking dependencies..."

    MISSING_DEPS=()
    for cmd in tar gzip curl; do
        if ! command -v "$cmd" &>/dev/null; then
            MISSING_DEPS+=("$cmd")
        fi
    done

    if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
        log "Installing missing packages: ${MISSING_DEPS[*]}"
        if command -v apt-get &>/dev/null; then
            sudo apt-get update -qq
            sudo apt-get install -y -qq "${MISSING_DEPS[@]}"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y -q "${MISSING_DEPS[@]}"
        elif command -v pacman &>/dev/null; then
            sudo pacman -Sy --noconfirm --needed "${MISSING_DEPS[@]}"
        else
            err "Cannot install dependencies automatically. Install: ${MISSING_DEPS[*]}"
            exit 1
        fi
    fi

    # Vulkan runtime (essential for UE5 Linux)
    if ! ldconfig -p | grep -q libvulkan; then
        log "Installing Vulkan runtime..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y -qq libvulkan1 vulkan-tools mesa-vulkan-drivers
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y -q vulkan-loader vulkan-tools mesa-vulkan-drivers
        elif command -v pacman &>/dev/null; then
            sudo pacman -Sy --noconfirm --needed vulkan-icd-loader vulkan-tools vulkan-radeon vulkan-intel
        fi
    fi

    ok "Dependencies satisfied"
    echo ""
fi

# ============================================================
# INSTALL FILES
# ============================================================
log "Installing ${PRODUCT_NAME} to ${PREFIX}..."

if [[ "$USER_INSTALL" == "false" ]]; then
    sudo mkdir -p "$PREFIX"
    sudo chown "$(id -u):$(id -g)" "$PREFIX"
else
    mkdir -p "$PREFIX"
fi

# Extract game files (assumes tarball in same dir)
TARBALL="${PRODUCT_NAME,,}-${PRODUCT_VERSION}-linux.tar.gz"
if [[ -f "$TARBALL" ]]; then
    tar -xzf "$TARBALL" -C "$PREFIX" --strip-components=1
    ok "Game files extracted"
else
    warn "Game tarball not found: $TARBALL"
    warn "Creating directory structure for manual install..."
    mkdir -p "$PREFIX/bin" "$PREFIX/citypacks" "$PREFIX/lib" "$PREFIX/share"
fi

# Install citypacks
if [[ -d "../../citypacks/akron-oh-beta-001" ]]; then
    cp -r "../../citypacks/akron-oh-beta-001" "$PREFIX/citypacks/"
    ok "Default citypack installed"
fi

# ============================================================
# DESKTOP INTEGRATION
# ============================================================
DESKTOP_FILE="$HOME/.local/share/applications/${PRODUCT_NAME,,}.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=${PRODUCT_NAME}
Comment=Real-world arcade racing in Unreal Engine 5
Exec=${PREFIX}/bin/${PRODUCT_NAME}
Icon=${PREFIX}/share/icons/racegps.png
Type=Application
Categories=Game;Simulation;SportsGame;
Terminal=false
StartupNotify=true
PrefersNonDefaultGPU=true
EOF

chmod +x "$DESKTOP_FILE"
ok "Desktop entry created: $DESKTOP_FILE"

# Symlink to PATH
if [[ "$USER_INSTALL" == "true" ]]; then
    mkdir -p "$HOME/.local/bin"
    ln -sf "${PREFIX}/bin/${PRODUCT_NAME}" "$HOME/.local/bin/${PRODUCT_NAME,,}"
fi

# ============================================================
# FIRST-RUN CONFIG
# ============================================================
CONFIG_DIR="$HOME/.config/${PRODUCT_NAME,,}"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/settings.json" <<EOF
{
  "version": "${PRODUCT_VERSION}",
  "install_path": "${PREFIX}",
  "first_run": true,
  "graphics_preset": "auto",
  "onboarding_complete": false,
  "selected_citypack": "akron-oh-beta-001"
}
EOF

# ============================================================
# DONE
# ============================================================
echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "  Location: ${PREFIX}"
echo "  Desktop:  ~/.local/share/applications/${PRODUCT_NAME,,}.desktop"
echo "  Config:   ~/.config/${PRODUCT_NAME,,}/"
echo ""
echo "  Next steps:"
echo "    1. Launch from your applications menu or run:"
echo "       ${PREFIX}/bin/${PRODUCT_NAME}"
echo "    2. On first run, the onboarding wizard will"
echo "       detect your hardware and configure settings."
echo ""

if [[ "$SKIP_PREFLIGHT" == "false" ]]; then
    read -rp "Launch ${PRODUCT_NAME} now? [Y/n]: " LAUNCH
    if [[ "$LAUNCH" =~ ^[Yy]$ ]] || [[ -z "$LAUNCH" ]]; then
        "${PREFIX}/bin/${PRODUCT_NAME}" &
    fi
fi
