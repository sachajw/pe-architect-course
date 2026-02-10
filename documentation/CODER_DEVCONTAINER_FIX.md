# Coder Tasks

## ✅ Resolved: Devcontainer Detection Error (Feb 10, 2026)

### Problem Description
Workspace `pangarabbit` showed a devcontainer error in `coder show` output:
```
Devcontainers
  └─ ✘ error
     × exit status 127
```

### Investigation
1. **Initial Health Check:** Deployed at https://sandbox.platformengineering.org/, user `sachawharton`
2. **Container Analysis:** Identified `wonderful_cray` container running `ghcr.io/coder/envbuilder:latest`
3. **Log Review:** Found errors related to Kubernetes cluster setup, but devcontainer-specific error was separate
4. **Root Cause Discovery:** Coder agent attempts to query devcontainer status via:
   ```bash
   envbuilder devcontainer status
   ```
   The `envbuilder` binary is installed at `/.envbuilder/bin/envbuilder` but this path is **not in the container's PATH**.

### Root Cause
The Coder agent's devcontainer detection relies on the `envbuilder` command being available in PATH. When it's not found, the command fails with exit code 127 (command not found), resulting in the error state.

### Solution

#### Immediate Fix (Temporary)
Created a symlink inside the running container:
```bash
docker exec wonderful_cray ln -sf /.envbuilder/bin/envbuilder /usr/local/bin/envbuilder
```

#### Permanent Fix
Added the symlink command to `.devcontainer/postCreateCommand.sh` so it persists across workspace rebuilds:

```bash
# Fix envbuilder PATH issue for Coder devcontainer detection
run_as_root ln -sf /.envbuilder/bin/envbuilder /usr/local/bin/envbuilder 2>/dev/null || true
```

This should be added after the Docker daemon setup section (around line 34).

### Verification
After applying the fix, `coder show pangarabbit` now shows:
```
└─ Devcontainers
   └─ ⏹ stopped
```

The "stopped" status is expected and correct - the error is resolved.

### Environment Details
| Setting | Value |
|---------|-------|
| Deployment | https://sandbox.platformengineering.org/ |
| Workspace | pangarabbit |
| Template | pe-course-architects |
| Agent | dev |
| CLI Version | v2.29.6 |
| Agent Version | v2.29.1+59cdd7e |

### Files Modified
- `.devcontainer/postCreateCommand.sh` - Added symlink creation command

### Related Issues
- Kind cluster `5min-idp` shows some errors in logs but cluster is functional
- Kubeconfig export needed manual intervention due to root ownership of state directory

---

## Pending Tasks

### Delete Old Workspace
Workspace `pe-course-cnoe` hasn't been built in 196+ days. Consider deleting if unused:
```bash
coder delete pe-course-cnoe
```
