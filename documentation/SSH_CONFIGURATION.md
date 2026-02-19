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

| Shortcut | Purpose | Auto-tmux | Port Forwards |
|----------|---------|-----------|---------------|
| `ssh pangarabbit.coder` | Zed, scripts, general | ❌ No | ✅ Yes |
| `ssh t.pangarabbit` | Terminal session | ✅ Yes | ✅ Yes |
| `ssh cap.pangarabbit` | Terminal + Capacitor | ✅ Yes | ✅ Yes |
| `ssh sync.pangarabbit` | File sync (rsync/scp) | ❌ No | ❌ No |
| `ssh proxy.pangarabbit` | SOCKS proxy | ❌ No | ❌ No |

> **Note:** `pangarabbit.coder` has NO `RemoteCommand` to work with Zed IDE. Use `t.pangarabbit` for terminal sessions with auto-tmux.

## Port Forwards

| Local Port | Remote Port | Service |
|------------|-------------|---------|
| 4739 | 4739 | Capacitor Dashboard |
| 3001 | 3000 | Grafana |
| 8000 | 8000 | Teams API |
| 4200 | 4200 | Teams Web UI |
| 8180 | 8180 | Keycloak SSO |

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

Use `t.pangarabbit` for terminal sessions with auto-tmux:

```bash
ssh t.pangarabbit  # Creates/attaches to session "main"
```

- Session persists across disconnects
- Reconnect to resume where you left off
- Use `Ctrl+B D` to detach (session keeps running)

**Why separate shortcuts?**
- `pangarabbit.coder` - NO auto-tmux (required for Zed, scripts)
- `t.pangarabbit` - WITH auto-tmux (for interactive terminal)

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
    ControlPersist 60
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes
    Compression yes
#### SSH Global Settings End ####

#### Coder Workspaces - Custom Configs ####
# Main host - NO RemoteCommand (required for Zed)
Host pangarabbit.coder
    User root
    LocalForward 4739 localhost:4739
    LocalForward 3001 localhost:3000
    LocalForward 8080 localhost:8080

# Terminal with auto-tmux
Host t.pangarabbit
    HostName pangarabbit.coder
    User root
    LocalForward 4739 localhost:4739
    RequestTTY yes
    RemoteCommand tmux new -A -s main

# SOCKS proxy
Host proxy.pangarabbit
    HostName pangarabbit.coder
    User root
    DynamicForward 1080
    RequestTTY no

# File sync (no TTY)
Host sync.pangarabbit
    HostName pangarabbit.coder
    User root
    RequestTTY no

# Capacitor focus
Host cap.pangarabbit
    HostName pangarabbit.coder
    User root
    LocalForward 4739 localhost:4739
    RequestTTY yes
    RemoteCommand cap-status && tmux new -A -s main
#### Coder Workspaces End ####
```

**Key Settings Explained:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `ControlPersist` | 60 | Auto-close background connections after 60s |
| `ServerAliveInterval` | 60 | Send keepalive every 60 seconds |
| `ServerAliveCountMax` | 3 | Disconnect after 3 missed keepalives |

## Local Cleanup Alias

Add to your local `~/.zshrc`:

```bash
# SSH cleanup alias
alias ssh-clean='pkill -f "ssh.*coder" 2>/dev/null; rm -f ~/.ssh/sockets/* 2>/dev/null; echo "SSH sockets cleaned"'
```

Usage:
```bash
ssh-clean    # Cleans stale sockets and kills hanging connections
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

### Stale Socket / Port Already in Use

**Symptoms:**
```
mux_client_forward: forwarding request failed: Port forwarding failed
bind [127.0.0.1]:4739: Address already in use
ControlSocket already exists, disabling multiplexing
```

**Quick Fix:**
```bash
# Clean up stale connections and sockets
ssh-clean

# Or manually:
pkill -f "ssh.*coder"
rm -f ~/.ssh/sockets/*
```

**Prevention:**
- `ControlPersist 60` - Auto-closes background connections after 60s
- Always use `Ctrl+B D` (tmux detach) or `~.` (SSH escape) to disconnect properly

### Connection Refused

```bash
# Check if workspace is running
coder list

# Restart workspace if needed
coder start pangarabbit
```

### Port Already in Use (Non-SSH)

```bash
# Find what's using the port
lsof -i :4739

# Kill the process
kill <PID>
```

### Tmux Session Issues

```bash
# List sessions
ssh sync.pangarabbit "tmux list-sessions"

# Kill session
ssh sync.pangarabbit "tmux kill-session -t main"
```

### Multiplexing Commands

```bash
# Check active connection
ssh -O check pangarabbit.coder

# Gracefully close background connection
ssh -O exit pangarabbit.coder

# Force cleanup
ssh-clean
```

## Quick Reference

```bash
# Zed / scripts / general use (no tmux)
ssh pangarabbit.coder

# Terminal with auto-tmux
ssh t.pangarabbit

# Quick command execution
ssh sync.pangarabbit "kubectl get pods"

# File transfer
scp file.txt sync.pangarabbit:/workspaces/persistent/

# SOCKS proxy
ssh -f -N proxy.pangarabbit

# Clean up stale connections
ssh-clean
```

## Usage Examples

### Daily Workflow

```bash
# Terminal session with tmux persistence
ssh t.pangarabbit
# → Opens in tmux session "main"
# → Port forwards active (4739, 3001, 8080)

# Detach but keep session running
Ctrl+B D

# Later: Reconnect to same session
ssh t.pangarabbit
# → Back where you left off
```

### Zed Remote Development

```bash
# Zed connects to pangarabbit.coder automatically
# No tmux interference - Zed can run commands freely
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
