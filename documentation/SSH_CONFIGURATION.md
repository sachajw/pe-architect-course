# SSH Configuration Guide

**Date:** February 19, 2026
**Environment:** Coder workspace (pangarabbit.coder)
**Status:** ✅ All features tested and verified

## Overview

This document covers the SSH configuration for connecting to your Coder workspace with enhanced features like auto-tmux, port forwarding, SOCKS proxy, and connection multiplexing.

## Verified Test Results

| Feature | Status | Notes |
|---------|--------|-------|
| Connection multiplexing | ✅ | Socket active at `~/.ssh/sockets/` |
| Auto-tmux | ✅ | Session "main" persists |
| SOCKS proxy | ✅ | Traffic routes through workspace IP |
| Port forwards | ✅ | 4739, 3000, 8080 active |
| SSH agent forwarding | ✅ | Git push works without keys |

## SSH Shortcuts

| Shortcut | Purpose | Features |
|----------|---------|----------|
| `ssh pangarabbit.coder` | Full connect | Auto-tmux, port forwards |
| `ssh cap.pangarabbit` | Capacitor mode | Auto-tmux + Capacitor status |
| `ssh proxy.pangarabbit` | SOCKS proxy | Browse through workspace |
| `ssh sync.pangarabbit` | File sync | No TTY, for rsync/scp |
| `ssh zed.pangarabbit` | Zed mode | Auto-tmux (zed session) |

## Port Forwards

| Local Port | Remote Port | Service |
|------------|-------------|---------|
| 4739 | 4739 | Capacitor Dashboard |
| 3000 | 3000 | Grafana / General |
| 8080 | 8080 | General Purpose |
| 8443 | 8443 | HTTPS |

## Connection Features

### 1. Connection Multiplexing ✅

Reuses existing SSH connections for instant new terminals:

```
~/.ssh/sockets/  # Socket files stored here
```

**Commands:**
```bash
# Check if multiplexed
ssh -O check pangarabbit.coder

# Close background connection
ssh -O exit pangarabbit.coder
```

### 2. Auto-Tmux ✅

Automatically creates/attaches to a tmux session on connect:

- `pangarabbit.coder` → session "main"
- `zed.pangarabbit` → session "zed"
- `cap.pangarabbit` → session "main"

Session persists across disconnects. Reconnect to resume where you left off.

**Tmux Quick Keys:**
| Keys | Action |
|------|--------|
| `Ctrl+B` `D` | Detach (keep session running) |
| `Ctrl+B` `C` | New window |
| `Ctrl+B` `N` | Next window |
| `Ctrl+B` `P` | Previous window |
| `Ctrl+B` `"` | Split horizontal |
| `Ctrl+B` `%` | Split vertical |
| `Ctrl+B` `[` | Enter copy mode |
| `Ctrl+B` `]` | Paste |

### 3. SSH Agent Forwarding ✅

Your local SSH keys are available on the remote for git operations:

```bash
# On workspace, can push to GitHub without copying keys
git push
```

### 4. SOCKS Proxy ✅

Browse the internet through your workspace:

```bash
# Start proxy in background
ssh -f -N proxy.pangarabbit

# Use with curl
curl --socks5 localhost:1080 https://ifconfig.me

# Configure browser SOCKS proxy:
# Host: localhost
# Port: 1080

# Stop proxy
pkill -f "ssh.*proxy.pangarabbit"
```

**Verified Results:**
- Direct IP: `197.89.115.194` (local)
- Via SOCKS: `35.198.165.220` (workspace)

**Use Cases:**
- Access internal Kubernetes services from local browser
- Browse as if you're in the workspace
- Bypass local network restrictions
- Test internal endpoints

### 5. File Sync

Quick rsync/scp operations:

```bash
# Sync local to remote
rsync -avz ./local-dir/ sync.pangarabbit:/workspaces/pe-coder-aidp/

# Copy file
scp ./file.txt sync.pangarabbit:/workspaces/persistent/

# Sync persistent storage
rsync -avz ~/.ccs/ sync.pangarabbit:/workspaces/persistent/.ccs/
```

## SSH Config Structure

Location: `~/.ssh/config`

```
#### SSH Global Settings ####
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes
    Compression yes
#### SSH Global Settings End ####

#### Coder Workspaces - Custom Configs ####
Host pangarabbit.coder
    User root
    LocalForward 4739 localhost:4739
    LocalForward 3000 localhost:3000
    LocalForward 8080 localhost:8080
    RequestTTY yes
    RemoteCommand tmux new -A -s main

Host proxy.pangarabbit
    HostName pangarabbit.coder
    User root
    DynamicForward 1080
    RequestTTY no

Host sync.pangarabbit
    HostName pangarabbit.coder
    User root
    RequestTTY no

Host zed.pangarabbit
    HostName pangarabbit.coder
    User root
    LocalForward 4739 localhost:4739
    RequestTTY yes
    RemoteCommand tmux new -A -s zed
#### Coder Workspaces End ####
```

## Zed Remote Development

Zed is configured with multiple projects and port forwards.

**Location:** `~/.config/zed/settings.json`

**Projects:**
- PE Coder AIDP (`/workspaces/pe-coder-aidp`)
- Persistent Storage (`/workspaces/persistent`)
- Root Home (`/root`)

**Usage:**
1. Open Zed
2. `Cmd+Shift+P` → "Remote Development: Open Remote Projects"
3. Select "pe architecture"
4. Choose a project

## SSH Escape Sequences

While connected, use these sequences (press Enter first):

| Sequence | Action |
|----------|--------|
| `~?` | Show help |
| `~.` | Disconnect |
| `~C` | Open command line (add/remove forwards) |
| `~&` | Background SSH |
| `~^Z` | Suspend SSH |

## Troubleshooting

### Connection Refused

```bash
# Check if workspace is running
coder list

# Restart workspace if needed
coder start pangarabbit
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :4739

# Kill the process
kill <PID>
```

### Stale Socket

```bash
# Remove stale socket
rm ~/.ssh/sockets/root@pangarabbit.coder-22
```

### Tmux Session Issues

```bash
# List sessions
ssh sync.pangarabbit "tmux list-sessions"

# Kill session
ssh sync.pangarabbit "tmux kill-session -t main"
```

## Quick Reference

```bash
# Connect with full features (auto-tmux)
ssh pangarabbit.coder

# Quick command execution (no tmux)
ssh sync.pangarabbit "kubectl get pods"

# File transfer
scp file.txt sync.pangarabbit:/workspaces/persistent/

# Start SOCKS proxy in background
ssh -f -N proxy.pangarabbit

# Check connection status
ssh -O check pangarabbit.coder

# Kill all sessions to workspace
pkill -f "ssh.*pangarabbit"
```

## Usage Examples

### Daily Workflow

```bash
# Morning: Connect with full features
ssh pangarabbit.coder
# → Opens in tmux session "main"
# → Port forwards active (4739, 3000, 8080)

# Detach but keep session running
Ctrl+B D

# Later: Reconnect to same session
ssh pangarabbit.coder
# → Back where you left off
```

### Quick Commands

```bash
# Check Capacitor status
ssh sync.pangarabbit "cap-status"

# View pods
ssh sync.pangarabbit "kubectl get pods -A"

# Run bootstrap after restart
ssh sync.pangarabbit "/workspaces/persistent/bootstrap.sh"
```

### File Operations

```bash
# Copy docs to workspace
scp -r ./documentation sync.pangarabbit:/workspaces/persistent/

# Sync CCS config
rsync -avz ~/.ccs/shared/ sync.pangarabbit:/workspaces/persistent/.ccs/shared/

# Download logs
scp sync.pangarabbit:/tmp/capacitor.log ./local-logs/
```

### Browse Through Workspace

```bash
# Start SOCKS proxy
ssh -f -N proxy.pangarabbit

# Access internal service
curl --socks5 localhost:1080 http://localhost:4739

# Browser: Set SOCKS proxy to localhost:1080
# Then access: http://localhost:4739 (Capacitor)

# Stop proxy when done
pkill -f "ssh.*proxy.pangarabbit"
```

---

**Related Documentation:**
- [CAPACITOR_ACCESS_GUIDE.md](./CAPACITOR_ACCESS_GUIDE.md)
- [ZSH_REMOTE_SETUP.md](./ZSH_REMOTE_SETUP.md)
- [bootstrap.sh](./bootstrap.sh)
