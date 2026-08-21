#!/usr/bin/env bash
# =============================================================================
# PREX Server Provisioning & Initialization Script
# =============================================================================
# Run this on a fresh Ubuntu 22.04 / 24.04 LTS server to prepare for PREX CD.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/<owner>/PREX/main/scripts/server-setup.sh | sudo bash
#   - OR -
#   sudo ./scripts/server-setup.sh
# =============================================================================

set -eo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[SETUP]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run this script with sudo or as root.${NC}"
    exit 1
fi

DEPLOY_DIR="/opt/prex"
DEPLOY_USER="${SUDO_USER:-$USER}"

log "Updating system packages..."
apt-get update -y && apt-get upgrade -y

log "Installing required baseline dependencies..."
apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw \
    fail2ban \
    htop \
    jq

# Install Docker CE if not already installed
if ! command -v docker &> /dev/null; then
    log "Installing Docker CE & Docker Compose plugin..."
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    mkdir -p /etc/docker
    cat <<EOF > /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  }
}
EOF
    systemctl restart docker
    success "Docker CE installed successfully."
fi

# Add deploy user to docker group
if [ -n "$DEPLOY_USER" ] && [ "$DEPLOY_USER" != "root" ]; then
    log "Adding user '${DEPLOY_USER}' to the docker group..."
    usermod -aG docker "$DEPLOY_USER"
fi

# Configure UFW Firewall
log "Configuring UFW Firewall rules..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
success "UFW Firewall configured."

# Create deployment directory
log "Setting up deployment directory at ${DEPLOY_DIR}..."
mkdir -p "${DEPLOY_DIR}"
if [ -n "$DEPLOY_USER" ] && [ "$DEPLOY_USER" != "root" ]; then
    chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${DEPLOY_DIR}"
fi

success "========================================================="
success "🎉 Server provisioning completed successfully!"
success "========================================================="
