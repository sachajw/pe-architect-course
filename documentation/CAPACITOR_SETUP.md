# Capacitor Next Installation Documentation

**Date:** February 8, 2025  
**Environment:** pe architecture (pangarabbit.coder)  
**Status:** ✅ Successfully Installed

## What is Capacitor Next?

Capacitor Next is a Kubernetes dashboard and GitOps tool from Gimlet.io that provides:

- 🎯 **Real-time Kubernetes cluster visualization**
- 📊 **Resource monitoring and management**
- 🚀 **GitOps workflow support**
- 🔍 **Cluster state inspection**
- 📦 **Deployment tracking**

## Installation Details

- **Binary Location:** `/usr/local/bin/next`
- **Binary Size:** 196MB
- **Version:** 0.14.0
- **Platform:** Linux x86_64
- **Installed:** January 5, 2026

## Installation Command Used

```bash
wget -qO- https://gimlet.io/install-capacitor | bash
```

## Quick Start

### Start Capacitor Next

```bash
# Basic start (localhost only)
next

# Start on all interfaces
next --host 0.0.0.0

# Custom port
next --port 8080

# With access logging
next --access-log
```

### Default Configuration

- **Host:** `localhost` (only accessible from within the container)
- **Port:** `4739`
- **Kubeconfig:** `/root/.kube/config`
- **Static Files:** `./web/static`

## Command-Line Options

```bash
Usage of next:
      --access-log                 Enable HTTP/WebSocket access logging
  -h, --host string                Host to listen on (default "localhost")
      --insecure-skip-tls-verify   Skip TLS certificate verification
      --kubeconfig string          Path to kubeconfig file (default "/root/.kube/config")
  -p, --port int                   Port to listen on (default 4739)
      --static-dir string          Directory for static files (default "./web/static")
```

## Environment Variables

You can also configure Capacitor using environment variables:

- `CAPACITOR_NEXT_HOST` - Host to listen on
- `CAPACITOR_NEXT_PORT` - Port to listen on
- `KUBECONFIG` - Path to kubeconfig file
- `KUBECONFIG_INSECURE_SKIP_TLS_VERIFY` - Skip TLS verification
- `ACCESS_LOG_ENABLED` - Enable access logging

## Using with Kind Cluster

Capacitor automatically uses your Kind cluster (5min-idp):

```bash
# Verify kubectl is working
kubectl cluster-info

# Start Capacitor (it will use the same kubeconfig)
next --host 0.0.0.0 --port 4739
```

## Access Capacitor UI

Since you're using Zed Remote SSH with port forwarding configured:

1. **Start Capacitor:**
   ```bash
   next --host 0.0.0.0 --port 4739
   ```

2. **Access in browser:**
   - If port 4739 is forwarded: `http://localhost:4739`
   - Otherwise, you'll need to add port forwarding

## Adding Port Forwarding for Capacitor

### Option 1: Update Zed Settings

Edit `~/.config/zed/settings.json` on your local machine:

```json
{
  "ssh_connections": [
    {
      "host": "pangarabbit.coder",
      "nickname": "pe architecture",
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

### Option 2: Manual SSH Port Forwarding

```bash
# From your local machine
ssh -L 4739:localhost:4739 pangarabbit.coder
```

### Option 3: SSH Tunnel in Background

```bash
# From your local machine
ssh -N -L 4739:localhost:4739 pangarabbit.coder &
```

## Running Capacitor in Background

### Using nohup

```bash
nohup next --host 0.0.0.0 --port 4739 > /tmp/capacitor.log 2>&1 &
echo $! > /tmp/capacitor.pid
```

### Stop Background Process

```bash
kill $(cat /tmp/capacitor.pid)
rm /tmp/capacitor.pid
```

### Using screen/tmux

```bash
# Using screen
screen -dmS capacitor next --host 0.0.0.0 --port 4739
screen -r capacitor  # Reattach to session

# Using tmux
tmux new -d -s capacitor 'next --host 0.0.0.0 --port 4739'
tmux attach -t capacitor  # Reattach to session
```

## Useful Aliases

Add these to your `~/.aliases`:

```bash
# Start Capacitor
alias cap-start='next --host 0.0.0.0 --port 4739'

# Start Capacitor in background
alias cap-bg='nohup next --host 0.0.0.0 --port 4739 > /tmp/capacitor.log 2>&1 & echo $! > /tmp/capacitor.pid'

# Stop Capacitor
alias cap-stop='kill $(cat /tmp/capacitor.pid 2>/dev/null) && rm /tmp/capacitor.pid'

# View Capacitor logs
alias cap-logs='tail -f /tmp/capacitor.log'

# Check if Capacitor is running
alias cap-status='ps aux | grep "[n]ext --host"'
```

## Integration with Kind Cluster

Capacitor will automatically detect and connect to your Kind cluster:

- **Cluster Name:** 5min-idp
- **API Server:** https://5min-idp-control-plane:6443
- **Nodes:** 1 control plane node
- **Namespaces:** default, kube-system, ingress-nginx, local-path-storage

## Features You Can Use

### 1. Cluster Overview
- View all namespaces
- See resource usage
- Monitor cluster health

### 2. Resource Management
- View/Edit Deployments, Pods, Services
- Real-time status updates
- Resource logs and events

### 3. GitOps Integration
- Track deployments from Git
- Monitor sync status
- View deployment history

### 4. Troubleshooting
- View pod logs in real-time
- Execute into containers
- Inspect resource definitions

## Troubleshooting

### Check if Capacitor is Running

```bash
ps aux | grep next
netstat -tlnp | grep 4739
```

### View Logs

```bash
# If running in background
tail -f /tmp/capacitor.log

# If running in foreground, check terminal output
```

### Connection Issues

```bash
# Verify kubeconfig is accessible
kubectl cluster-info

# Test Capacitor can reach cluster
next --insecure-skip-tls-verify --host 0.0.0.0
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :4739

# Kill the process
kill $(lsof -t -i:4739)

# Or use a different port
next --host 0.0.0.0 --port 5000
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Localhost Only (Default):** By default, Capacitor only binds to localhost for security
2. **Expose Carefully:** Only use `--host 0.0.0.0` in trusted environments
3. **Port Forwarding:** Use SSH port forwarding instead of exposing directly
4. **TLS Verification:** Avoid `--insecure-skip-tls-verify` in production

## Uninstalling

To remove Capacitor:

```bash
rm /usr/local/bin/next
```

## Additional Resources

- **Official Site:** https://gimlet.io
- **Documentation:** https://gimlet.io/docs
- **GitHub:** https://github.com/gimlet-io/capacitor
- **Community:** Join Gimlet Discord/Slack

## Quick Reference

```bash
# Start Capacitor
next --host 0.0.0.0 --port 4739

# Access UI
http://localhost:4739

# Stop (if running in foreground)
Ctrl+C

# Check version/help
next  # Shows usage
```

## Integration with Your Workflow

Capacitor complements your existing tools:

- **kubectl** - Command-line cluster management
- **k9s** - Terminal-based UI (if installed)
- **Capacitor** - Web-based dashboard and GitOps

Use whichever tool fits your current task best!

---

**Documentation created:** February 8, 2025  
**Ready to use** ✓