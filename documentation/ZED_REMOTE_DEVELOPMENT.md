# Zed Remote Development Setup Guide

**Date:** February 8, 2025  
**Environment:** pe architecture (pangarabbit.coder)  
**Status:** ✅ Fully Configured

## Overview

Zed's Remote Development feature allows you to edit code on a remote server while running Zed locally. The UI stays responsive because it runs on your machine, while language servers, tasks, and terminals run on the server.

## Why Zed Remote SSH?

✅ **Lightweight** - Much faster and less resource-intensive than VS Code  
✅ **Native SSH** - Uses standard SSH configuration  
✅ **Port Forwarding** - Built-in support for forwarding ports  
✅ **Fast** - Minimal latency, optimized protocol  
✅ **Secure** - All traffic encrypted through SSH  
✅ **No Container Required** - Direct SSH connection to server

## Current Configuration

### Connection Details

- **Host:** `pangarabbit.coder`
- **Nickname:** `pe architecture`
- **User:** `root` (via Coder SSH config)
- **Workspace Path:** `/workspaces/pe-coder-aidp`
- **Shell:** `zsh` (with Starship prompt)

### Configuration Location

**Local Machine:** `~/.config/zed/settings.json` (Mac/Linux)

```json
{
  "ssh_connections": [
    {
      "host": "pangarabbit.coder",
      "nickname": "pe architecture",
      "args": [],
      "projects": [
        {
          "paths": [
            "/workspaces/pe-coder-aidp"
          ]
        }
      ],
      "port_forwards": [
        {
          "local_port": 8443,
          "remote_port": 8443
        },
        {
          "local_port": 4739,
          "remote_port": 4739
        }
      ]
    }
  ]
}
```

## How It Works

### Architecture

```
┌─────────────────┐         SSH          ┌──────────────────┐
│   Local Mac     │◄──────────────────►  │  Remote Server   │
│                 │                       │                  │
│  Zed UI         │                       │  Zed Headless    │
│  File Browser   │                       │  Language Server │
│  Settings       │                       │  Terminal        │
│  Extensions     │                       │  File System     │
└─────────────────┘                       └──────────────────┘
        │                                          │
        │                                          │
        └──────────── Synchronized ────────────────┘
```

### What Runs Where

#### Local (Your Mac)
- ✅ Zed UI/Editor interface
- ✅ Syntax highlighting (Tree-sitter)
- ✅ AI features (Claude integration)
- ✅ Keyboard shortcuts
- ✅ Unsaved changes buffer
- ✅ Project history

#### Remote (pangarabbit.coder)
- ✅ Source code files
- ✅ Language servers (LSP)
- ✅ Terminal sessions
- ✅ Build/test tasks
- ✅ Git operations
- ✅ File system operations

## Connecting to Remote

### Method 1: Command Palette (Recommended)

1. **Open Zed**
2. **Press:** `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Linux/Windows)
3. **Type:** `remote projects`
4. **Select:** "Remote Development: Open Remote Projects"
5. **Click:** "pe architecture"
6. **Wait** for connection to establish
7. **Done!** - You're connected

### Method 2: Recent Projects

1. **Press:** `Cmd+Ctrl+Shift+O` (Mac)
2. **Select:** "pe architecture" from the list
3. **Press:** Enter

### Method 3: Connect New Server

1. **Press:** `Cmd+Shift+P`
2. **Type:** `remote connect`
3. **Select:** "Remote Development: Connect to a Server over SSH"
4. **Enter:** `pangarabbit.coder`
5. **Choose path:** `/workspaces/pe-coder-aidp`

## SSH Configuration

### Coder SSH Setup

Your SSH config (`~/.ssh/config`) includes Coder integration:

```
# ------------START-CODER-----------
Host *.coder
    ConnectTimeout=0
    StrictHostKeyChecking=no
    UserKnownHostsFile=/dev/null
    LogLevel ERROR

Match host *.coder !exec "/opt/homebrew/bin/coder connect exists %h"
    ProxyCommand /opt/homebrew/bin/coder --global-config "/Users/tvl/Library/Application Support/coderv2" ssh --stdio --hostname-suffix coder %h
# ------------END-CODER------------
```

This enables `pangarabbit.coder` to resolve through the Coder CLI.

### Connection Process

1. Zed reads `pangarabbit.coder` from settings
2. SSH config routes through Coder CLI
3. Coder CLI authenticates and connects to workspace
4. Zed downloads/updates remote server binary if needed
5. Connection established

## Port Forwarding

### Configured Ports

| Local Port | Remote Port | Purpose |
|------------|-------------|---------|
| 8443 | 8443 | Workshop services (from devcontainer.json) |
| 4739 | 4739 | Capacitor Kubernetes Dashboard |

### How Port Forwarding Works

```
Your Browser (localhost:4739)
    │
    ▼
SSH Tunnel (encrypted)
    │
    ▼
Remote Service (pangarabbit.coder:4739)
    │
    ▼
Capacitor Next
```

### Adding More Port Forwards

Edit `~/.config/zed/settings.json`:

```json
{
  "port_forwards": [
    {
      "local_port": 8080,
      "remote_port": 8080
    }
  ]
}
```

Then **reconnect** Zed Remote SSH for changes to take effect.

### Testing Port Forwarding

```bash
# On local machine, check if port is listening
lsof -nP -iTCP:4739 | grep LISTEN

# Test connection
curl http://localhost:4739
```

## Remote Server Binary

### Location on Remote

```
~/.zed_server/zed-remote-server-stable-<VERSION>
```

### Automatic Updates

Zed automatically:
- Downloads server binary on first connect
- Updates when your local Zed version changes
- Matches server version to client version

### Manual Server Management

```bash
# Check server version (on remote)
ls -lh ~/.zed_server/

# Remove server (forces redownload)
rm -rf ~/.zed_server/
```

## Settings & Configuration

### Local Settings vs Remote Settings

#### Local Settings (`~/.config/zed/settings.json` - Your Mac)
Used for:
- UI preferences (theme, font size)
- Keyboard shortcuts
- SSH connections
- Port forwarding
- Window behavior

#### Remote Settings (`~/.config/zed/settings.json` - Remote Server)
Used for:
- Language server configurations
- Formatter settings
- Project-specific settings
- File associations

#### Project Settings (`.zed/settings.json` in project)
Used for:
- Team-shared settings
- Indentation rules
- Language-specific formatting
- File patterns

### Syncing Settings

Settings are **NOT** automatically synced. To sync:

```bash
# Copy local settings to remote (if desired)
scp ~/.config/zed/settings.json pangarabbit.coder:~/.config/zed/settings.json
```

## Extensions

### Extension Behavior

Extensions installed locally are **automatically propagated** to the remote server.

This means:
- Language servers run on remote
- Features work correctly
- No manual installation needed

### Checking Extensions

**On Local:**
1. Open Zed
2. `Cmd+Shift+P` → "Extensions"
3. View installed extensions

**On Remote:**
```bash
ls ~/.local/share/zed/extensions/
```

## Terminal Integration

### Opening Terminals

Terminals opened in Zed run on the **remote server**.

1. **Press:** ``Ctrl+` `` or `Cmd+J`
2. **Or:** Terminal → New Terminal
3. **Shell:** Uses remote default (`zsh`)

### Features Available

✅ Full zsh with Starship prompt  
✅ All aliases (`k`, `kg`, `cap-start`, etc.)  
✅ kubectl access to Kind cluster  
✅ Docker commands  
✅ Git operations  
✅ File system access

### Multiple Terminals

- Each terminal is a separate SSH session
- They share the remote environment
- Scroll back history preserved

## File Operations

### Opening Files

All file operations happen on the remote:
- Open/Edit - Remote files
- Save - Writes to remote
- Search - Searches remote filesystem
- File browser - Shows remote tree

### Unsaved Changes

Unsaved changes are stored **locally** by default. If connection drops:
- Your unsaved work is safe
- Reconnect to continue
- Zed will restore unsaved buffers

### Git Operations

Git operations run on the remote:
- `git status` shows remote repo state
- Commits happen on remote
- Push/pull use remote credentials

## Performance

### Optimizations

Zed Remote SSH is optimized for:
- Low latency editing
- Efficient file transfer
- Minimal bandwidth usage
- Fast language server responses

### Network Requirements

- **Minimum:** Stable SSH connection
- **Recommended:** Low-latency network (< 100ms)
- **Bandwidth:** Minimal (mostly text data)

### Troubleshooting Slow Performance

1. **Check SSH latency:**
   ```bash
   ssh pangarabbit.coder "echo connected"
   # Should be instant
   ```

2. **Check remote resources:**
   ```bash
   ssh pangarabbit.coder "top -bn1 | head -20"
   ```

3. **Restart Zed server:**
   - Disconnect from remote
   - Reconnect (server restarts)

## Troubleshooting

### Connection Issues

#### "Failed to connect to remote server"

**Causes:**
- SSH connection failure
- Network issues
- Server binary download failed

**Solutions:**
```bash
# Test SSH directly
ssh pangarabbit.coder "echo test"

# Check Coder CLI
coder list

# Check SSH config
cat ~/.ssh/config | grep -A 5 "coder"
```

#### "Connection timeout"

**Solutions:**
1. Check network connectivity
2. Restart Coder CLI: `coder logout && coder login`
3. Try manual SSH: `ssh pangarabbit.coder`

### Port Forwarding Not Working

**Symptoms:**
- `http://localhost:4739` doesn't connect
- Browser shows "connection refused"

**Solutions:**

1. **Reconnect Zed:**
   - Disconnect and reconnect to reset port forwarding

2. **Verify remote service is running:**
   ```bash
   ssh pangarabbit.coder "cap-status"
   ```

3. **Check local port:**
   ```bash
   lsof -i :4739
   # Should show Zed or ssh process
   ```

4. **Manual SSH tunnel (backup):**
   ```bash
   ssh -N -L 4739:localhost:4739 pangarabbit.coder
   ```

### File Changes Not Showing

**Symptom:** Changes made remotely (via SSH) don't appear in Zed

**Solution:**
1. **Refresh file tree:** Right-click → Refresh
2. **Or:** Reconnect Zed

### Terminal Not Working

**Symptoms:**
- Terminal doesn't open
- Commands don't execute

**Solutions:**
1. Check terminal logs: `Cmd+Shift+P` → "Open Log"
2. Verify shell exists: `ssh pangarabbit.coder "which zsh"`
3. Try different shell temporarily

### Extensions Not Working

**Symptom:** Language features not working

**Solutions:**
1. Check extension installed locally
2. Check remote logs: `ssh pangarabbit.coder "cat ~/.local/share/zed/logs/*"`
3. Reinstall extension locally

## Disconnecting

### Graceful Disconnect

1. **Save all files**
2. **Press:** `Cmd+Shift+P`
3. **Type:** `disconnect`
4. **Select:** "Remote Development: Disconnect from Server"

### What Happens

- SSH connection closed
- Port forwarding stopped
- Remote server process remains (for fast reconnect)
- Local Zed continues running

### Reconnecting

Simply connect again using any method above. The remote server daemon will reattach.

## Best Practices

### 1. Save Regularly

While unsaved changes are buffered locally, save often:
- `Cmd+S` - Save current file
- `Cmd+K S` - Save all files

### 2. Use Port Forwarding

Instead of exposing services externally, use port forwarding:
- Secure (encrypted through SSH)
- Easy to manage
- No firewall changes needed

### 3. Close Unused Terminals

Terminals keep SSH sessions alive:
- Close when done
- Reduces resource usage

### 4. Commit and Push Regularly

Work is on the remote server:
- Commit to git frequently
- Push to remote repository
- Protects against remote server issues

### 5. Monitor Resources

Watch remote resource usage:
```bash
ssh pangarabbit.coder "htop"
```

### 6. Keep Zed Updated

Update regularly for:
- Bug fixes
- Performance improvements
- New features

## Advanced Configuration

### Custom SSH Arguments

Add to Zed settings:

```json
{
  "ssh_connections": [
    {
      "host": "pangarabbit.coder",
      "args": ["-v"],  // Verbose logging
      "port": 22,
      "username": "root"
    }
  ]
}
```

### Upload Binary Over SSH

For restricted networks:

```json
{
  "ssh_connections": [
    {
      "host": "pangarabbit.coder",
      "upload_binary_over_ssh": true
    }
  ]
}
```

### Multiple Projects

```json
{
  "projects": [
    {
      "paths": ["/workspaces/pe-coder-aidp"]
    },
    {
      "paths": ["/workspaces/another-project"]
    }
  ]
}
```

## Comparison with Other Methods

### vs SSHFS

| Feature | Zed Remote SSH | SSHFS |
|---------|---------------|-------|
| Speed | Fast (native) | Slower (filesystem overhead) |
| Setup | Simple | Complex (macFUSE, mounting) |
| Reliability | High | Can stall |
| Resources | Low | Medium |
| **Recommendation** | ✅ **Use This** | Backup option |

### vs VS Code Remote

| Feature | Zed | VS Code |
|---------|-----|---------|
| Resource Usage | Low | High |
| Speed | Fast | Slower |
| Setup | Simple | More complex |
| Extensions | Growing | Mature |
| **Use Case** | Fast editing | Full IDE features |

## Security Considerations

✅ **Encrypted** - All traffic through SSH  
✅ **Key-based auth** - No password transmission  
✅ **Port forwarding** - Secure local access  
✅ **No external exposure** - Services stay private  
⚠️ **Trust remote server** - Code execution on server  
⚠️ **Network security** - Use trusted networks

### Best Practices

1. Use SSH keys (no passwords)
2. Keep SSH client updated
3. Use VPN on untrusted networks
4. Monitor SSH sessions
5. Log out when done

## Resources

- **Zed Remote Docs:** https://zed.dev/docs/remote-development
- **SSH Documentation:** `man ssh`
- **Coder CLI:** `coder --help`
- **Zed Community:** https://zed.dev/community

## Quick Reference

```bash
# Connect to remote
Cmd+Shift+P → "remote projects" → "pe architecture"

# Disconnect
Cmd+Shift+P → "disconnect"

# Open terminal
Ctrl+` or Cmd+J

# Access Capacitor
http://localhost:4739

# Test SSH
ssh pangarabbit.coder "echo test"

# Check ports
lsof -i :4739
```

## Summary

### What You Have

✅ Zed configured for remote SSH  
✅ Connection to `pangarabbit.coder`  
✅ Port forwarding for Capacitor (4739)  
✅ Auto-propagated extensions  
✅ Terminal with zsh/Starship  
✅ Fast, lightweight editing

### When to Use

- ✅ **Use Zed Remote SSH when:**
  - You want fast, responsive editing
  - Resource usage matters
  - You need port forwarding
  - Simple setup is important

- ⚠️ **Consider alternatives when:**
  - You need heavy IDE features
  - Extensive debugging required
  - VS Code extensions are mandatory

---

**Configuration:** `~/.config/zed/settings.json`  
**Documentation:** https://zed.dev/docs/remote-development  
**Last Updated:** February 8, 2025 ✓