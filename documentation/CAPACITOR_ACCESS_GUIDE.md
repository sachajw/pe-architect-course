# Capacitor Next - Local Browser Access Guide

**Date:** February 8, 2025  
**Environment:** pe architecture (pangarabbit.coder)  
**Remote Port:** 4739  
**Local Port:** 4739

## Overview

Capacitor Next is running on your remote environment and listening on port **4739**. This guide shows you how to access the web UI from your local browser using port forwarding.

## Current Status

✅ **Capacitor is running** on remote at `0.0.0.0:4739`  
✅ **Port forwarding configured** in Zed settings  
✅ **Ready to access** via `http://localhost:4739`

## Method 1: Zed's Built-in Port Forwarding (Recommended)

Zed Remote SSH includes automatic port forwarding. This is the easiest method.

### Step 1: Verify Configuration

Your Zed settings already include port forwarding:

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

Location: `~/.config/zed/settings.json`

### Step 2: Reconnect Zed Remote SSH

Port forwarding activates when you connect to the remote server.

**If already connected, you need to reconnect:**

1. **Open Command Palette:** Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Linux/Windows)
2. **Type:** `remote disconnect` or `disconnect`
3. **Select:** "Remote Development: Disconnect from Server"
4. **Wait** for disconnection to complete

**Then reconnect:**

1. **Open Command Palette:** `Cmd+Shift+P`
2. **Type:** `remote projects`
3. **Select:** "Remote Development: Open Remote Projects"
4. **Click:** "pe architecture"
5. **Wait** for connection to establish

### Step 3: Verify Port Forwarding is Active

**On your local machine**, check if port 4739 is listening:

```bash
# macOS/Linux
lsof -nP -iTCP:4739 | grep LISTEN

# Or using netstat
netstat -an | grep 4739

# Should see something like:
# TCP    127.0.0.1:4739    0.0.0.0:0    LISTENING
```

### Step 4: Open Browser

Simply open your browser and navigate to:

```
http://localhost:4739
```

You should see the **Capacitor Kubernetes Dashboard**!

### Troubleshooting Zed Port Forwarding

**Port forwarding not working?**

1. **Check Zed version:** Ensure you're using Zed v0.159 or later
2. **Check settings syntax:** Verify JSON is valid (no trailing commas)
3. **Restart Zed completely:** Quit and reopen the application
4. **Check Zed logs:**
   - `Cmd+Shift+P` → "Open Log"
   - Search for "port forward" or "4739"

**Still not working?**

Use Method 2 (Manual SSH Port Forwarding) below.

---

## Method 2: Manual SSH Port Forwarding

If Zed's port forwarding doesn't work, use standard SSH tunneling.

### Option A: Quick Command

Open a **new terminal** on your local machine and run:

```bash
ssh -N -L 4739:localhost:4739 pangarabbit.coder
```

**Explanation:**
- `-N` - Don't execute remote commands (just forward port)
- `-L 4739:localhost:4739` - Forward local port 4739 to remote port 4739
- Keep this terminal open while using Capacitor
- Press `Ctrl+C` to stop forwarding

### Option B: Background Process

Run port forwarding in the background:

```bash
# Start in background
ssh -f -N -L 4739:localhost:4739 pangarabbit.coder

# Check it's running
ps aux | grep "ssh.*4739"

# Stop when done
pkill -f "ssh.*4739.*pangarabbit"
```

### Option C: Using SSH Config

Add to your `~/.ssh/config`:

```
Host pangarabbit-capacitor
    HostName pangarabbit.coder
    LocalForward 4739 localhost:4739
    User root
```

Then connect:

```bash
ssh pangarabbit-capacitor
```

### Access Browser

Once port forwarding is active, open:

```
http://localhost:4739
```

---

## Method 3: Using Coder CLI (Alternative)

Since you're using Coder workspaces, you can also use Coder's port forwarding:

```bash
# List available ports
coder port-forward pangarabbit --tcp 4739:4739
```

Then access at `http://localhost:4739`

---

## Verification Steps

### 1. Check Capacitor is Running on Remote

```bash
# From local machine, SSH and check
ssh pangarabbit.coder "capacitor-status"

# Or
ssh pangarabbit.coder "ps aux | grep next"
```

Should show Capacitor running with PID.

### 2. Test Remote Endpoint

```bash
# Curl the remote endpoint
ssh pangarabbit.coder "curl -s http://localhost:4739 | head -10"
```

Should return HTML (the Capacitor web app).

### 3. Check Local Port Forwarding

```bash
# On your local machine
lsof -i :4739

# Or
netstat -an | grep 4739
```

Should show port 4739 is listening locally.

### 4. Test Local Access

```bash
# From your local machine
curl http://localhost:4739

# Should return HTML
```

---

## What You Should See

When you successfully access `http://localhost:4739`, you'll see:

### Capacitor Dashboard Features:

1. **Cluster Overview**
   - Cluster name: `kind-5min-idp`
   - Node status
   - Resource usage

2. **Namespaces**
   - default
   - kube-system
   - ingress-nginx
   - local-path-storage

3. **Resources by Namespace**
   - Deployments
   - Pods
   - Services
   - ConfigMaps
   - Secrets
   - etc.

4. **Real-time Updates**
   - Live pod status
   - Resource changes
   - Event stream

5. **Resource Details**
   - Click any resource to see details
   - View YAML
   - See events
   - View logs

---

## Troubleshooting

### Issue: "Connection Refused" or "Unable to Connect"

**Cause:** Port forwarding not active or Capacitor not running

**Solutions:**

1. **Check Capacitor is running:**
   ```bash
   ssh pangarabbit.coder "capacitor-status"
   ```

2. **Restart Capacitor:**
   ```bash
   ssh pangarabbit.coder "cap-restart"
   ```

3. **Verify port forwarding** (see verification steps above)

4. **Try manual SSH tunnel:**
   ```bash
   ssh -N -L 4739:localhost:4739 pangarabbit.coder
   ```

### Issue: "Site Can't Be Reached" or "ERR_CONNECTION_RESET"

**Cause:** Wrong URL or port

**Solutions:**

1. **Use correct URL:** `http://localhost:4739` (not https)
2. **Check port number:** Must be 4739
3. **Try 127.0.0.1:** `http://127.0.0.1:4739`

### Issue: Blank Page or 404

**Cause:** Capacitor might not be fully started

**Solutions:**

1. **Check logs:**
   ```bash
   ssh pangarabbit.coder "tail -50 /tmp/capacitor.log"
   ```

2. **Restart Capacitor:**
   ```bash
   ssh pangarabbit.coder "cap-restart"
   ```

3. **Wait 10 seconds** for full startup

4. **Hard refresh browser:** `Cmd+Shift+R` or `Ctrl+Shift+R`

### Issue: Port 4739 Already in Use Locally

**Cause:** Another process using port 4739 on your local machine

**Solutions:**

1. **Find what's using it:**
   ```bash
   lsof -i :4739
   ```

2. **Kill the process:**
   ```bash
   kill <PID>
   ```

3. **Or use different local port:**
   ```bash
   # Forward local 5000 to remote 4739
   ssh -N -L 5000:localhost:4739 pangarabbit.coder
   
   # Access at http://localhost:5000
   ```

### Issue: "Connection Timeout"

**Cause:** Network issues or SSH connection dropped

**Solutions:**

1. **Test SSH connection:**
   ```bash
   ssh pangarabbit.coder "echo 'Connection OK'"
   ```

2. **Reconnect Zed Remote SSH**

3. **Check network connectivity**

4. **Try manual SSH tunnel** to bypass Zed

---

## Quick Reference

### Start Port Forwarding (Manual)

```bash
# Foreground (keep terminal open)
ssh -N -L 4739:localhost:4739 pangarabbit.coder

# Background
ssh -f -N -L 4739:localhost:4739 pangarabbit.coder
```

### Access URL

```
http://localhost:4739
```

### Check Status

```bash
# Remote Capacitor status
ssh pangarabbit.coder "cap-status"

# Local port check
lsof -i :4739

# Test connection
curl http://localhost:4739
```

### Stop Port Forwarding

```bash
# If running in foreground: Ctrl+C

# If running in background:
pkill -f "ssh.*4739.*pangarabbit"
```

---

## Alternative Access Methods

### 1. Direct SSH with Browser Redirect

Some terminals support clickable links:

```bash
ssh pangarabbit.coder -L 4739:localhost:4739 -t "echo 'Access Capacitor at http://localhost:4739' && bash"
```

### 2. Using VS Code (If You Have It)

VS Code also supports port forwarding:

1. Connect to remote via VS Code Remote SSH
2. Ports panel → Forward a Port
3. Enter: 4739
4. Access at `http://localhost:4739`

### 3. SSH Config with Auto-Forward

Add to `~/.ssh/config`:

```
Host pangarabbit.coder
    LocalForward 4739 localhost:4739
```

Now any SSH connection will auto-forward:

```bash
ssh pangarabbit.coder
# Port 4739 automatically forwarded
```

---

## Security Considerations

✅ **Secure:** Port forwarding through SSH is encrypted  
✅ **Local only:** Capacitor only accessible on your machine  
✅ **No external exposure:** Port 4739 not exposed to internet  
⚠️ **No authentication:** Capacitor itself has no auth (relies on SSH)

**Best Practices:**

1. Only forward ports when needed
2. Close SSH tunnels when done
3. Don't forward to `0.0.0.0` on local machine
4. Keep SSH keys secure

---

## Summary

### Recommended Method: Zed Port Forwarding

1. Ensure Zed settings have port forwarding configured ✅ (already done)
2. Disconnect and reconnect Zed Remote SSH
3. Open `http://localhost:4739` in browser
4. Done! 🎉

### Backup Method: Manual SSH

```bash
ssh -N -L 4739:localhost:4739 pangarabbit.coder
```

Then open `http://localhost:4739`

---

## Getting Help

If you're still having issues:

1. **Check Capacitor logs:**
   ```bash
   ssh pangarabbit.coder "cap-logs"
   ```

2. **Verify Kind cluster is healthy:**
   ```bash
   ssh pangarabbit.coder "kubectl get nodes"
   ```

3. **Test direct SSH:**
   ```bash
   ssh pangarabbit.coder "curl -v http://localhost:4739"
   ```

4. **Check Zed documentation:**
   https://zed.dev/docs/remote-development#port-forwarding

---

**Documentation created:** February 8, 2025  
**Ready to access Capacitor!** ✓