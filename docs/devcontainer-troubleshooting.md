# DevContainer Troubleshooting Guide

## Issue: "exit status 127 devcontainer result is not json"

### Symptoms
When attempting to build or run the devcontainer, the following error occurs:
```
exit status 127 devcontainer result is not json: ""
```

### Root Cause
The **devcontainer CLI** (`@devcontainers/cli`) was not installed on the Coder workspace. Exit status 127 is a standard Unix error code meaning "command not found".

### Diagnosis Steps
```bash
# Check if devcontainer CLI is installed
which devcontainer
# Expected: /usr/local/bin/devcontainer
# If empty or "not found", the CLI is missing

# Check if Node.js/npm are available (required for devcontainer CLI)
which node npm
```

### Solution

#### Step 1: Install Node.js and npm
```bash
sudo apt-get update
sudo apt-get install -y nodejs npm
```

#### Step 2: Install the DevContainer CLI
```bash
npm install -g @devcontainers/cli
```

#### Step 3: Verify Installation
```bash
devcontainer --version
# Expected output: 0.83.2 (or later version)
```

#### Step 4: Test DevContainer Build
```bash
cd /workspaces/pe-coder-aidp
devcontainer build --workspace-folder .
```

### Permanent Fix for Coder Workspaces

To ensure the devcontainer CLI is available in new workspaces, add the following to your Coder template or workspace provisioning script:

```hcl
# In Coder template (main.tf)
resource "coder_script" "devcontainer_cli" {
  agent_id = coder_agent.main.id
  display_name = "Install DevContainer CLI"
  icon = "/icons/docker.svg"
  script = <<-EOT
    #!/bin/bash
    sudo apt-get update
    sudo apt-get install -y nodejs npm
    sudo npm install -g @devcontainers/cli
  EOT
  run_on_start = true
}
```

Alternatively, add to the devcontainer's `postCreateCommand.sh`:

```bash
# Check if devcontainer CLI is installed
if ! command -v devcontainer &> /dev/null; then
  echo "devcontainer CLI not found. Installing..."
  run_as_root apt-get install -y nodejs npm
  sudo npm install -g @devcontainers/cli
fi
```

### Related Files

| File | Purpose |
|------|---------|
| `.devcontainer/devcontainer.json` | DevContainer configuration |
| `.devcontainer/postCreateCommand.sh` | Post-creation setup script |

### Common Exit Codes Reference

| Code | Meaning |
|------|---------|
| 127 | Command not found |
| 126 | Command not executable |
| 1 | General error |
| 0 | Success |

### Verification Commands

```bash
# Check devcontainer CLI
devcontainer --version

# List installed npm packages
npm list -g @devcontainers/cli

# Test build
devcontainer build --workspace-folder . --dry-run
```

---

**Date:** 2026-02-20  
**Environment:** pangarabbit.coder (Coder workspace)  
**DevContainer CLI Version:** 0.83.2  
**Node.js Version:** 18.19.1
