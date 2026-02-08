# SSHFS Setup Guide for macOS

## Overview

This guide explains how to set up SSHFS (SSH Filesystem) to mount remote directories from `pangarabbit.coder` on your local Mac, allowing tools like Zed to access remote files as if they were local.

## Initial Installation (Already Completed)

The following packages have been installed:

```bash
# macFUSE - Required kernel extension
brew install --cask macfuse

# SSHFS for macOS
brew install gromgit/fuse/sshfs-mac
```

## After Reboot Steps

### 1. Approve macFUSE Kernel Extension

1. Go to **System Settings → Privacy & Security**
2. Look for a message about "System software from developer Benjamin Fleischer"
3. Click **Allow** or **Open** to approve the kernel extension
4. You may need to restart again after approving

### 2. Verify Installation

```bash
# Check if SSHFS is available
which sshfs

# Verify kernel extension is loaded
kextstat | grep -i fuse

# Check SSHFS version
sshfs --version
```

### 3. Create Mount Point

```bash
# Create directory for mounting (if not already exists)
mkdir -p ~/mounts/pangarabbit
```

### 4. Mount Remote Directory

**Basic mount command:**
```bash
sshfs pangarabbit.coder:/workspaces/pe-coder-aidp ~/mounts/pangarabbit
```

**Recommended mount with performance options:**
```bash
sshfs pangarabbit.coder:/workspaces/pe-coder-aidp ~/mounts/pangarabbit \
  -o volname=pangarabbit \
  -o follow_symlinks \
  -o auto_cache \
  -o reconnect \
  -o defer_permissions \
  -o noappledouble \
  -o ServerAliveInterval=15 \
  -o ServerAliveCountMax=3
```

### 5. Verify Mount

```bash
# Check if mounted
mount | grep pangarabbit

# List remote files
ls ~/mounts/pangarabbit

# Test access
ls -la ~/mounts/pangarabbit
```

### 6. Open in Zed

```bash
# Open the mounted directory in Zed
zed ~/mounts/pangarabbit

# Or navigate and open
cd ~/mounts/pangarabbit
zed .
```

## Mount Options Explained

- `volname=pangarabbit` - Sets a friendly name for the volume
- `follow_symlinks` - Follow symbolic links on the remote system
- `auto_cache` - Enable automatic caching for better performance
- `reconnect` - Automatically reconnect if connection drops
- `defer_permissions` - Better permission handling on macOS
- `noappledouble` - Prevent creation of `.AppleDouble` and `._` files
- `ServerAliveInterval=15` - Send keepalive packets every 15 seconds
- `ServerAliveCountMax=3` - Disconnect after 3 failed keepalive attempts

## Unmounting

### Normal Unmount
```bash
umount ~/mounts/pangarabbit
```

### Using diskutil (macOS)
```bash
diskutil unmount ~/mounts/pangarabbit
```

### Force Unmount (if frozen)
```bash
diskutil unmount force ~/mounts/pangarabbit
# or
umount -f ~/mounts/pangarabbit
```

## Auto-Mount Script (Optional)

Create a helper script to quickly mount:

```bash
# Create script directory
mkdir -p ~/bin

# Create mount script
cat > ~/bin/mount-pangarabbit.sh << 'EOF'
#!/bin/bash

MOUNT_POINT="$HOME/mounts/pangarabbit"
REMOTE="pangarabbit.coder:/workspaces/pe-coder-aidp"

# Check if already mounted
if mount | grep -q "$MOUNT_POINT"; then
  echo "✓ Already mounted at $MOUNT_POINT"
  exit 0
fi

# Ensure mount point exists
mkdir -p "$MOUNT_POINT"

# Mount with SSHFS
echo "Mounting $REMOTE to $MOUNT_POINT..."
sshfs "$REMOTE" "$MOUNT_POINT" \
  -o volname=pangarabbit \
  -o follow_symlinks \
  -o auto_cache \
  -o reconnect \
  -o defer_permissions \
  -o noappledouble \
  -o ServerAliveInterval=15 \
  -o ServerAliveCountMax=3

if [ $? -eq 0 ]; then
  echo "✓ Successfully mounted!"
  ls "$MOUNT_POINT"
else
  echo "✗ Mount failed"
  exit 1
fi
EOF

# Make executable
chmod +x ~/bin/mount-pangarabbit.sh
```

**Usage:**
```bash
~/bin/mount-pangarabbit.sh
```

## Unmount Script (Optional)

```bash
# Create unmount script
cat > ~/bin/unmount-pangarabbit.sh << 'EOF'
#!/bin/bash

MOUNT_POINT="$HOME/mounts/pangarabbit"

if ! mount | grep -q "$MOUNT_POINT"; then
  echo "Not mounted"
  exit 0
fi

echo "Unmounting $MOUNT_POINT..."
diskutil unmount "$MOUNT_POINT" 2>/dev/null || umount "$MOUNT_POINT"

if [ $? -eq 0 ]; then
  echo "✓ Successfully unmounted"
else
  echo "Failed to unmount, trying force..."
  diskutil unmount force "$MOUNT_POINT"
fi
EOF

# Make executable
chmod +x ~/bin/unmount-pangarabbit.sh
```

**Usage:**
```bash
~/bin/unmount-pangarabbit.sh
```

## Troubleshooting

### Kernel Extension Not Loaded

If you get errors about FUSE not being available:

```bash
# Check if extension is loaded
kextstat | grep -i fuse

# Manually load extension (may require reboot)
sudo kextload /Library/Filesystems/macfuse.fs/Contents/Extensions/*/macfuse.kext
```

### Permission Denied

Try adding the `defer_permissions` option:
```bash
sshfs pangarabbit.coder:/workspaces/pe-coder-aidp ~/mounts/pangarabbit -o defer_permissions
```

### Mount Point Busy or Already Mounted

```bash
# Force unmount first
diskutil unmount force ~/mounts/pangarabbit

# Then try mounting again
```

### Connection Drops Frequently

Increase keepalive frequency:
```bash
sshfs pangarabbit.coder:/workspaces/pe-coder-aidp ~/mounts/pangarabbit \
  -o ServerAliveInterval=10 \
  -o ServerAliveCountMax=5 \
  -o reconnect
```

### Slow Performance

Try these options:
```bash
sshfs pangarabbit.coder:/workspaces/pe-coder-aidp ~/mounts/pangarabbit \
  -o Ciphers=aes128-ctr \
  -o Compression=no \
  -o cache=yes \
  -o kernel_cache
```

### Stale Mount (Unresponsive)

```bash
# Kill any hanging SSHFS processes
pkill -9 sshfs

# Force unmount
diskutil unmount force ~/mounts/pangarabbit

# Remove and recreate mount point
rm -rf ~/mounts/pangarabbit
mkdir -p ~/mounts/pangarabbit

# Try mounting again
```

## Quick Reference

```bash
# Mount
sshfs pangarabbit.coder:/workspaces/pe-coder-aidp ~/mounts/pangarabbit

# Check status
mount | grep pangarabbit

# Unmount
diskutil unmount ~/mounts/pangarabbit

# Open in Zed
zed ~/mounts/pangarabbit
```

## Remote System Details

- **Host:** `pangarabbit.coder`
- **Remote Path:** `/workspaces/pe-coder-aidp`
- **Local Mount Point:** `~/mounts/pangarabbit`
- **User:** `root` (via SSH)

## Notes

- The mounted filesystem will appear in Finder as a network volume
- Files are accessed over SSH, so network latency affects performance
- Changes made locally are immediately synced to the remote system
- Keep the terminal window open if you want to see any error messages
- Remember to unmount before shutting down to prevent issues

## Alternative: Zed Remote Development

If SSHFS doesn't work well, consider using Zed's built-in remote development:

1. Open Zed
2. Press `Cmd+Shift+P`
3. Search for "Remote: Connect to Host"
4. Enter `pangarabbit.coder`
5. Work directly on remote files through Zed

## Resources

- [macFUSE Documentation](https://github.com/osxfuse/osxfuse/wiki)
- [SSHFS Documentation](https://github.com/libfuse/sshfs)
- [Zed Remote Development](https://zed.dev/docs/remote-development)