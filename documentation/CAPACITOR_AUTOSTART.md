# Capacitor Auto-Start Documentation

**Date:** February 8, 2025  
**Environment:** pe architecture (pangarabbit.coder)  
**Status:** ✅ Fully Configured

## Overview

Capacitor Next is now configured to automatically start when you connect to your remote development environment. It provides a web-based Kubernetes dashboard for your Kind cluster.

## What Was Configured

1. ✅ **Auto-start on shell login** - Capacitor starts when first shell opens
2. ✅ **Management scripts** - Easy start/stop/status commands
3. ✅ **Shell aliases** - Quick access commands
4. ✅ **Port forwarding** - Access from local browser via Zed
5. ✅ **Background execution** - Runs without blocking terminal

## Auto-Start Configuration

### Location
Auto-start code added to: `~/.zshrc`

### How It Works
- Runs only on **first shell** (`SHLVL -eq 1`)
- Checks if Capacitor is **already running**
- Starts in **background** with logging
- Sets `CAPACITOR_STARTED` environment variable

### Auto-Start Code
```bash
if [[ -z "$CAPACITOR_STARTED" && $SHLVL -eq 1 ]]; then
    export CAPACITOR_STARTED=1
    if ! pgrep -f "next --kubeconfig" > /dev/null; then
        nohup next --kubeconfig=/root/.kube/config \
          --host 0.0.0.0 --port 4739 > /tmp/capacitor.log 2>&1 &
        echo $! > /tmp/capacitor.pid
    fi
fi
```

## Management Commands

### Start/Stop/Status Scripts

Three management scripts are installed in `/usr/local/bin/`:

#### 1. `capacitor-start`
Starts Capacitor if not already running.

```bash
capacitor-start
```

**Features:**
- ✅ Checks if already running
- ✅ Validates kubeconfig exists
- ✅ Logs to `/tmp/capacitor.log`
- ✅ Saves PID to `/tmp/capacitor.pid`
- ✅ Verifies successful startup

#### 2. `capacitor-stop`
Stops Capacitor gracefully.

```bash
capacitor-stop
```

**Features:**
- ✅ Graceful shutdown (SIGTERM)
- ✅ Force kill if needed (SIGKILL)
- ✅ Cleans up PID file
- ✅ Handles stale PIDs

#### 3. `capacitor-status`
Shows current status and info.

```bash
capacitor-status
```

**Output includes:**
- Running status (✅ or ❌)
- Process ID
- Port and URL
- CPU/Memory usage
- Recent log entries
- Helpful commands

## Quick Access Aliases

Convenient aliases added to `~/.aliases`:

```bash
cap-start      # Start Capacitor
cap-stop       # Stop Capacitor
cap-status     # Check status
cap-logs       # View logs (tail -f)
cap-restart    # Stop and start
```

### Usage Examples

```bash
# Check if running
cap-status

# View live logs
cap-logs

# Restart Capacitor
cap-restart

# Stop Capacitor
cap-stop
```

## Configuration Details

### Capacitor Settings
- **Binary:** `/usr/local/bin/next`
- **Kubeconfig:** `/root/.kube/config`
- **Host:** `0.0.0.0` (all interfaces)
- **Port:** `4739`
- **Log File:** `/tmp/capacitor.log`
- **PID File:** `/tmp/capacitor.pid`

### Kubernetes Connection
- **Cluster:** `kind-5min-idp`
- **API Server:** `https://5min-idp-control-plane:6443`
- **Context:** `kind-5min-idp` (auto-detected)

## Port Forwarding (Zed)

Port forwarding is configured in your Zed settings to access Capacitor from your local browser.

### Configuration
Location: `~/.config/zed/settings.json`

```json
{
  "ssh_connections": [
    {
      "host": "pangarabbit.coder",
      "nickname": "pe architecture",
      "port_forwards": [
        {
          "local_port": 4739,
          "remote_port": 4739
        }
      ]
    }
  ]
}
```

### Accessing Capacitor UI

Once Capacitor is running and you're connected via Zed Remote SSH:

1. **Open browser on your local machine**
2. **Navigate to:** `http://localhost:4739`
3. **You'll see the Capacitor dashboard**

## Verification

### Check Auto-Start Works

1. **Disconnect from remote** (close Zed or SSH)
2. **Reconnect via Zed Remote SSH**
3. **Wait a moment** for auto-start
4. **Run:** `cap-status`

You should see:
```
Status: ✅ Running
PID: <process_id>
Port: 4739
URL: http://localhost:4739
```

### Check Port Forwarding

1. **Ensure Capacitor is running:** `cap-status`
2. **Open browser:** `http://localhost:4739`
3. **Should see:** Capacitor dashboard

## Log Files

### View Logs

```bash
# Live log viewing
cap-logs
# or
tail -f /tmp/capacitor.log

# Last 50 lines
tail -50 /tmp/capacitor.log

# Search logs
grep ERROR /tmp/capacitor.log
```

### Log Content

Logs include:
- Startup messages
- Connection to Kubernetes cluster
- HTTP server status
- API requests (if access logging enabled)
- Errors and warnings

## Troubleshooting

### Capacitor Not Starting

```bash
# Check status
cap-status

# Try manual start
capacitor-start

# Check logs for errors
tail -50 /tmp/capacitor.log

# Verify kubeconfig
kubectl cluster-info
```

### Port Already in Use

```bash
# Find what's using port 4739
lsof -i :4739

# Stop Capacitor
cap-stop

# Kill conflicting process
kill <pid>

# Start Capacitor again
cap-start
```

### Can't Access from Browser

**Check Capacitor is running:**
```bash
cap-status
```

**Check port forwarding:**
1. Disconnect from Zed Remote SSH
2. Reconnect (port forwarding reestablishes)
3. Try accessing again: `http://localhost:4739`

**Manual SSH tunnel (alternative):**
```bash
# From your local machine
ssh -L 4739:localhost:4739 pangarabbit.coder
```

### Stale PID File

```bash
# Status shows "stale PID file"
cap-status

# Clean up
rm /tmp/capacitor.pid

# Start fresh
cap-start
```

### Process Not Stopping

```bash
# Force stop
kill -9 $(cat /tmp/capacitor.pid)
rm /tmp/capacitor.pid

# Verify stopped
ps aux | grep next
```

## Disabling Auto-Start

If you want to disable auto-start:

### Temporary (Current Session)
```bash
export CAPACITOR_STARTED=1
```

### Permanent
```bash
# Edit .zshrc
vi ~/.zshrc

# Comment out or remove the auto-start section:
#### Capacitor Auto-Start ####
# ... (comment out this entire section)
#### Capacitor Auto-Start End ####

# Reload
source ~/.zshrc
```

## Manual Management

If you prefer manual control:

```bash
# Disable auto-start (see above)

# Start manually when needed
cap-start

# Stop when done
cap-stop
```

## Resource Usage

Capacitor typically uses:
- **CPU:** 0.5-2% (idle)
- **Memory:** ~50-100MB
- **Network:** Minimal (only cluster queries)

### Check Resources
```bash
cap-status  # Shows CPU/Memory in output

# Detailed info
ps aux | grep next

# Monitor in real-time
top -p $(cat /tmp/capacitor.pid)
```

## Advanced Configuration

### Custom Port

Edit auto-start in `~/.zshrc`:
```bash
# Change port from 4739 to 5000
--port 5000
```

Update Zed port forwarding to match.

### Enable Access Logging

```bash
# Stop Capacitor
cap-stop

# Edit capacitor-start script
sudo vi /usr/local/bin/capacitor-start

# Add --access-log flag
--access-log

# Start again
cap-start
```

### Custom Kubeconfig

If using different kubeconfig:
```bash
# Edit capacitor-start script
sudo vi /usr/local/bin/capacitor-start

# Change KUBECONFIG variable
KUBECONFIG="/path/to/custom/kubeconfig"
```

## Integration with Workflow

Capacitor complements your existing tools:

| Tool | Use Case | When to Use |
|------|----------|-------------|
| `kubectl` / `k` | Quick CLI operations | Fast checks, scripts |
| Capacitor | Visual exploration | Understanding cluster state |
| Zed Terminal | Development work | Coding, debugging |

## Security Notes

⚠️ **Important:**

1. **Localhost binding:** Using `0.0.0.0` allows access from any interface
2. **SSH tunnel:** Port forwarding through SSH is secure
3. **No authentication:** Capacitor has no built-in auth (relies on SSH)
4. **Trusted environment:** Only use in trusted networks

## Files Modified/Created

### Created Files
- `/usr/local/bin/capacitor-start` - Start script
- `/usr/local/bin/capacitor-stop` - Stop script
- `/usr/local/bin/capacitor-status` - Status script

### Modified Files
- `~/.zshrc` - Auto-start configuration
- `~/.aliases` - Convenience aliases
- `~/.config/zed/settings.json` - Port forwarding (local)

### Runtime Files
- `/tmp/capacitor.log` - Log output
- `/tmp/capacitor.pid` - Process ID

## Quick Reference

```bash
# Status
cap-status

# Start
cap-start

# Stop
cap-stop

# Restart
cap-restart

# Logs
cap-logs

# Access UI
http://localhost:4739
```

## Next Steps

1. ✅ **Reconnect to remote** - Auto-start will trigger
2. ✅ **Check status** - Run `cap-status`
3. ✅ **Open browser** - Navigate to `http://localhost:4739`
4. ✅ **Explore cluster** - Use Capacitor dashboard

---

**Documentation created:** February 8, 2025  
**Capacitor auto-start is ready!** ✓