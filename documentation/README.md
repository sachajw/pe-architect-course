# PE Architecture - Remote Development Environment Documentation

**Environment:** pe architecture (pangarabbit.coder)  
**Last Updated:** February 8, 2025  
**Status:** ✅ Fully Configured

## Overview

This directory contains comprehensive documentation for your remote Platform Engineering development environment. All setup, configuration, and usage guides are centralized here.

## 📚 Documentation Index

### Getting Started

1. **[SESSION_STATE.md](./SESSION_STATE.md)**
   - Session resume guide
   - Quick reference for what's been set up
   - Next steps after reboot/reconnect

### Remote Development Environment

2. **[ZED_REMOTE_DEVELOPMENT.md](./ZED_REMOTE_DEVELOPMENT.md)** ⭐ **START HERE**
   - Complete Zed Remote SSH setup guide
   - Connection configuration
   - Port forwarding setup
   - Troubleshooting and best practices
   - Performance optimization

3. **[SSHFS_SETUP_GUIDE.md](./SSHFS_SETUP_GUIDE.md)**
   - Alternative: SSHFS mounting (backup method)
   - Not recommended - use Zed Remote SSH instead

### Shell & Terminal Configuration

4. **[ZSH_REMOTE_SETUP.md](./ZSH_REMOTE_SETUP.md)**
   - Zsh installation and configuration
   - Shell aliases and functions
   - Environment variables
   - Kubernetes and Docker shortcuts

5. **[STARSHIP_CONFIGURATION.md](./STARSHIP_CONFIGURATION.md)**
   - Starship prompt setup and customization
   - Module configuration (git, kubernetes, docker, etc.)
   - Performance tuning
   - Troubleshooting prompt issues

### Kubernetes Dashboard (Capacitor)

6. **[CAPACITOR_SETUP.md](./CAPACITOR_SETUP.md)**
   - Capacitor Next installation guide
   - Basic usage and configuration
   - Command-line options
   - Integration with Kind cluster

7. **[CAPACITOR_AUTOSTART.md](./CAPACITOR_AUTOSTART.md)**
   - Auto-start configuration
   - Management scripts (start/stop/status)
   - Aliases and shortcuts
   - Logging and troubleshooting

8. **[CAPACITOR_ACCESS_GUIDE.md](./CAPACITOR_ACCESS_GUIDE.md)**
   - Accessing Capacitor from local browser
   - Port forwarding setup (Zed and manual)
   - Troubleshooting connection issues
   - Alternative access methods

## 🚀 Quick Start

### Connect to Environment

**Using Zed (Recommended):**
1. Open Zed
2. `Cmd+Shift+P` → "Remote Projects"
3. Select "pe architecture"
4. Navigate to `/workspaces/pe-coder-aidp`

**Read:** [ZED_REMOTE_DEVELOPMENT.md](./ZED_REMOTE_DEVELOPMENT.md) for complete guide

### Common Commands

```bash
# Documentation Access
docs                    # cd to documentation directory
readme                  # View README with glow (formatted)
list-docs              # List all documentation files

# Shell Management
szsh                    # Reload zsh configuration
ezsh                    # Edit zsh configuration

# Kubernetes (kubectl aliases)
k get pods              # Get pods (k = kubectl)
kg nodes                # Get nodes (kg = kubectl get)
kd pod <name>           # Describe pod (kd = kubectl describe)

# Docker
dps                     # Docker ps
di                      # Docker images

# Capacitor Dashboard
cap-status              # Check Capacitor status
cap-start               # Start Capacitor
cap-stop                # Stop Capacitor
cap-logs                # View Capacitor logs

# Git
g status                # Git status (g = git)
ga .                    # Git add (ga = git add)
gc -m "message"         # Git commit (gc = git commit)
```

### Access Web Services

**Capacitor Dashboard:**
- URL: `http://localhost:4739`
- Requires port forwarding via Zed (configured)
- See [CAPACITOR_ACCESS_GUIDE.md](./CAPACITOR_ACCESS_GUIDE.md)

## 🛠️ What's Installed

### Development Tools
- ✅ **Zsh** - Default shell with Starship prompt
- ✅ **Starship** - Beautiful, informative prompt
- ✅ **kubectl** - Kubernetes CLI
- ✅ **docker** - Docker CLI (Docker-in-Docker)
- ✅ **kind** - Kubernetes in Docker
- ✅ **terraform** - Infrastructure as Code
- ✅ **helm** - Kubernetes package manager
- ✅ **yq** - YAML processor
- ✅ **score-k8s** - Score implementation for K8s
- ✅ **Capacitor Next** - Kubernetes dashboard

### Kubernetes Cluster
- **Name:** 5min-idp
- **Type:** Kind (Kubernetes in Docker)
- **Version:** v1.32.0
- **Nodes:** 1 control plane
- **Registry:** Local registry on port 5001

### Web Services
- **Capacitor Next** - Port 4739 (Kubernetes dashboard)
- **Ingress NGINX** - Ports 80/443 (mapped to 30080/30443)

## 📁 Directory Structure

```
/workspaces/pe-coder-aidp/
├── documentation/          # ← YOU ARE HERE - All documentation
├── .devcontainer/          # DevContainer configuration
├── setup/                  # Setup scripts and configs
└── workshop/               # Workshop materials and exercises
```

## 🔧 Configuration Files

### Zed (Local Machine)
- `~/.config/zed/settings.json` - Zed settings with SSH config

### Shell Configuration (Remote)
- `~/.zshrc` - Main zsh configuration
- `~/.aliases` - Command aliases
- `~/.functions` - Shell functions
- `~/.exports` - Environment variables
- `~/.config/starship.toml` - Starship prompt config

### Kubernetes (Remote)
- `~/.kube/config` - Kubeconfig for Kind cluster
- `/home/vscode/state/kube/config-internal.yaml` - Internal kubeconfig

### Capacitor (Remote)
- `/usr/local/bin/next` - Capacitor binary
- `/usr/local/bin/capacitor-*` - Management scripts
- `/tmp/capacitor.log` - Capacitor logs
- `/tmp/capacitor.pid` - Capacitor process ID

## 🎯 Common Tasks

### View Cluster Resources

```bash
# Get all pods across namespaces
kg pods -A

# Get services
kg svc -A

# Describe a node
kd node 5min-idp-control-plane

# Check cluster info
k cluster-info
```

### Use Capacitor Dashboard

1. Ensure running: `cap-status`
2. If stopped: `cap-start`
3. Open browser: `http://localhost:4739`
4. Explore your Kind cluster visually

### Check Logs

```bash
# Capacitor logs
cap-logs

# Pod logs
kl <pod-name>

# Follow logs
kl -f <pod-name>
```

### Manage Capacitor

```bash
# Check status
cap-status

# Start/Stop/Restart
cap-start
cap-stop
cap-restart

# View logs
cap-logs
```

## 🆘 Troubleshooting

### Can't Access Capacitor Dashboard

1. Check if running: `cap-status`
2. Check logs: `cap-logs`
3. Restart: `cap-restart`
4. See [CAPACITOR_ACCESS_GUIDE.md](./CAPACITOR_ACCESS_GUIDE.md)

### Shell Aliases Not Working

```bash
# Reload shell
szsh

# Check if loaded
alias | grep kubectl
```

### Kubectl Not Working

```bash
# Check cluster is up
docker ps | grep kind

# Check kubeconfig
k cluster-info

# Get nodes
k get nodes
```

### Port Forwarding Issues

1. Reconnect Zed Remote SSH
2. Check [ZED_REMOTE_DEVELOPMENT.md](./ZED_REMOTE_DEVELOPMENT.md)
3. Try manual tunnel: `ssh -N -L 4739:localhost:4739 pangarabbit.coder`

### Zed Connection Issues

See complete troubleshooting in [ZED_REMOTE_DEVELOPMENT.md](./ZED_REMOTE_DEVELOPMENT.md#troubleshooting)

## 📖 Additional Resources

### Official Documentation
- [Zed Remote Development](https://zed.dev/docs/remote-development)
- [Starship Prompt](https://starship.rs/)
- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Capacitor GitHub](https://github.com/gimlet-io/capacitor)

### Internal Workshop Materials
- See `../workshop/` directory for exercises and labs

## 💡 Tips & Best Practices

1. **Use Zed Remote SSH** - Much better than SSHFS
2. **Use aliases** - `k`, `kg`, `kd` are faster than full kubectl commands
3. **Use Capacitor** - Visual exploration is easier for complex resources
4. **Check logs** - `cap-logs` and `kl` are your friends for debugging
5. **Reload config** - Run `szsh` after changing shell configs
6. **Port forwarding** - Reconnect Zed if port forwarding stops working
7. **Documentation here** - All docs in `/workspaces/pe-coder-aidp/documentation`

## 🔄 Documentation Guidelines

### All Documentation Lives Here

**Location:** `/workspaces/pe-coder-aidp/documentation/`

### Quick Access
```bash
# Navigate to docs
docs

# List all docs
list-docs

# View main README
readme

# View specific doc in terminal
glow STARSHIP_CONFIGURATION.md

# Edit in Zed
# Just browse to documentation/ folder in file explorer
```

### Adding New Documentation

1. Create `.md` file in this directory
2. Add entry to this README
3. Commit to git
4. Update "Last Updated" date

### File Naming Convention
- Use UPPERCASE with underscores: `MY_NEW_GUIDE.md`
- Be descriptive: `KUBERNETES_DEBUGGING.md` not `K8S.md`
- Use consistent structure

## 📝 Contributing

Found an issue or have improvements? 

1. Update the relevant documentation file
2. Update this README if adding new documentation
3. Test your changes
4. Commit with clear description
5. Share with the team

---

**📍 Documentation Location:** `/workspaces/pe-coder-aidp/documentation/`  
**🚀 Quick Access:** `docs` (alias) or browse in Zed file explorer  
**📖 Total Files:** 9 documentation files  
**✨ Last Updated:** February 8, 2025 ✓
