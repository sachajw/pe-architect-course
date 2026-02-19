#!/usr/bin/env bash
set -e

# Get script directory (works with bash and zsh)
if [ -n "${BASH_SOURCE[0]}" ]; then
  BOOTSTRAP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  BOOTSTRAP_DIR="/workspaces/persistent"
fi
PERSISTENT_DIR="/workspaces/persistent"

echo "🚀 Bootstrapping workspace..."

# Create directories
mkdir -p $PERSISTENT_DIR/.config
mkdir -p $PERSISTENT_DIR/.ccs/shared
mkdir -p $PERSISTENT_DIR/.agents/skills
mkdir -p $PERSISTENT_DIR/bin
mkdir -p /root/.config

# Copy CCS config from bootstrap dir if present (and not same location)
if [ -d "$BOOTSTRAP_DIR/ccs-config" ] && [ "$BOOTSTRAP_DIR" != "$PERSISTENT_DIR" ]; then
  echo "Setting up CCS config..."
  cp -r $BOOTSTRAP_DIR/ccs-config/* $PERSISTENT_DIR/.ccs/
fi

# Copy aliases file if present (and not same location)
if [ -f "$BOOTSTRAP_DIR/.aliases" ] && [ "$BOOTSTRAP_DIR" != "$PERSISTENT_DIR" ]; then
  echo "Setting up aliases..."
  cp $BOOTSTRAP_DIR/.aliases $PERSISTENT_DIR/
fi

# Restore starship config (if it exists and not same location)
if [ -f "$BOOTSTRAP_DIR/starship.toml" ] && [ "$BOOTSTRAP_DIR" != "$PERSISTENT_DIR" ]; then
  echo "Setting up starship..."
  cp $BOOTSTRAP_DIR/starship.toml $PERSISTENT_DIR/.config/
fi
ln -sf $PERSISTENT_DIR/.config/starship.toml /root/.config/starship.toml

# Install Claude CLI if not present
if ! command -v claude &> /dev/null; then
  echo "Installing Claude CLI..."
  curl -fsSL https://claude.ai/install.sh | bash
fi

# Install CCS CLI if not present
if ! command -v ccs &> /dev/null; then
  echo "Installing CCS CLI..."
  # Check if npm is available
  if command -v npm &> /dev/null; then
    npm install -g @anthropic/ccs 2>/dev/null || echo "CCS install via npm failed, skipping..."
  fi
fi

# Install Capacitor (Kubernetes dashboard) if not present
if ! command -v next &> /dev/null; then
  echo "Installing Capacitor..."
  curl -sL https://gimlet.io/install-capacitor | bash
fi

# Install lsd (modern ls) if not present
if ! command -v lsd &> /dev/null; then
  echo "Installing lsd..."
  apt-get update -qq && apt-get install -y lsd 2>/dev/null || echo "lsd install failed, skipping..."
fi

# Install dust (modern du) if not present
if ! command -v dust &> /dev/null; then
  echo "Installing dust..."
  apt-get install -y dust 2>/dev/null || echo "dust install failed, skipping..."
fi

# Symlink cc and agents dirs
ln -sf $PERSISTENT_DIR/.ccs /root/.ccs 2>/dev/null || true
ln -sf $PERSISTENT_DIR/.agents /root/.agents 2>/dev/null || true

# Add aliases source to zshrc if not present
if ! grep -q 'source /workspaces/persistent/.aliases' /root/.zshrc 2>/dev/null; then
  echo "Adding aliases source to zshrc..."
  cat >> /root/.zshrc << 'ALIASES_SRC'

# Load persisted aliases
[ -f /workspaces/persistent/.aliases ] && source /workspaces/persistent/.aliases
ALIASES_SRC
fi

# Ensure starship init is in zshrc
if ! grep -q 'starship init' /root/.zshrc 2>/dev/null; then
  cat >> /root/.zshrc << 'STARSHIP'

eval "$(starship init zsh)"
STARSHIP
fi

# Add Capacitor auto-start to zshrc if not present
if ! grep -q 'CAPACITOR_STARTED' /root/.zshrc 2>/dev/null; then
  echo "Adding Capacitor auto-start to zshrc..."
  cat >> /root/.zshrc << 'CAPACITOR'

#### Capacitor Auto-Start ####
if [[ -z "$CAPACITOR_STARTED" && $SHLVL -eq 1 ]]; then
    export CAPACITOR_STARTED=1
    if ! pgrep -f "next --kubeconfig" > /dev/null; then
        nohup next --kubeconfig=/root/.kube/config \
          --host 0.0.0.0 --port 4739 > /tmp/capacitor.log 2>&1 &
        echo $! > /tmp/capacitor.pid
        echo "Capacitor started on port 4739"
    fi
    # Grafana port-forward
    if ! pgrep -f "port-forward.*grafana" > /dev/null; then
        nohup kubectl port-forward -n monitoring svc/grafana-stack 3000:80 > /tmp/grafana-forward.log 2>&1 &
        echo "Grafana forwarded to localhost:3000"
    fi
    # Teams API port-forward
    if ! pgrep -f "port-forward.*teams-api" > /dev/null; then
        nohup kubectl port-forward -n teams-api svc/teams-api-service 8000:8000 > /tmp/teams-api-forward.log 2>&1 &
        echo "Teams API forwarded to localhost:8000"
    fi
    # Teams Web UI port-forward
    if ! pgrep -f "port-forward.*teams-ui" > /dev/null; then
        nohup kubectl port-forward -n engineering-platform svc/teams-ui-service 4200:80 > /tmp/teams-ui-forward.log 2>&1 &
        echo "Teams Web UI forwarded to localhost:4200"
    fi
    # Keycloak port-forward
    if ! pgrep -f "port-forward.*keycloak-service" > /dev/null; then
        nohup kubectl port-forward -n keycloak svc/keycloak-service 8180:8080 > /tmp/keycloak-forward.log 2>&1 &
        echo "Keycloak forwarded to localhost:8180"
    fi
fi
#### Capacitor Auto-Start End ####
CAPACITOR
fi

# Add persistent bin to PATH
if ! grep -q 'persistent/bin' /root/.zshrc 2>/dev/null; then
  echo 'export PATH="/workspaces/persistent/bin:$PATH"' >> /root/.zshrc
fi

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "📋 Quick Reference:"
echo "   cap-status     - Check Capacitor status"
echo "   cap-start      - Start Capacitor"
echo "   cap-stop       - Stop Capacitor"
echo "   cap-logs       - View Capacitor logs"
echo ""
echo "   Run: source ~/.zshrc"
