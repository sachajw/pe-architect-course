# Zsh Remote Setup Documentation

**Date:** February 8, 2025  
**Environment:** pe architecture (pangarabbit.coder)  
**Status:** ✅ Fully Configured

## What Was Configured

Your remote development environment now has a fully configured zsh shell with:

1. ✅ **Zsh as default shell** - Changed from bash to zsh
2. ✅ **Starship prompt** - Beautiful, informative prompt with git/k8s/docker context
3. ✅ **Custom aliases** - Kubernetes, Docker, Git, and Terraform shortcuts
4. ✅ **Useful functions** - Productivity helpers for common tasks
5. ✅ **Environment variables** - Optimized for cloud/k8s development

## Files Created

All configuration files are in the home directory (`~`):

- `~/.zshrc` - Main zsh configuration
- `~/.exports` - Environment variables and PATH settings
- `~/.aliases` - Command aliases
- `~/.functions` - Shell functions
- `~/.config/starship.toml` - Starship prompt configuration

## Quick Start

### Reload Configuration

After making changes to any config file:

```bash
# Reload zsh configuration
szsh
# or
source ~/.zshrc
```

### Edit Configuration

```bash
# Edit zsh config
ezsh
# or
vi ~/.zshrc

# Edit aliases
vi ~/.aliases

# Edit exports
vi ~/.exports

# Edit functions
vi ~/.functions

# Edit Starship prompt
vi ~/.config/starship.toml
```

## Useful Aliases

### Kubernetes
```bash
k          # kubectl
kg         # kubectl get
kd         # kubectl describe
kdel       # kubectl delete
kl         # kubectl logs
kx         # kubectl exec -it
kns        # kubectl config set-context --current --namespace
kctx       # kubectl config use-context
```

### Docker
```bash
d          # docker
dc         # docker-compose
dps        # docker ps
dpsa       # docker ps -a
di         # docker images
dlog       # docker logs
dexec      # docker exec -it
```

### Git
```bash
g          # git
gs         # git status
ga         # git add
gc         # git commit
gp         # git push
gl         # git log --oneline
gd         # git diff
gb         # git branch
gco        # git checkout
```

### Terraform
```bash
tf         # terraform
tfi        # terraform init
tfp        # terraform plan
tfa        # terraform apply
tfd        # terraform destroy
```

### Navigation
```bash
..         # cd ..
...        # cd ../..
....       # cd ../../..
l          # ls -la
ll         # ls -lh
c          # clear
```

## Useful Functions

### Directory Management
```bash
mkcd <dirname>        # Create directory and cd into it
```

### Archive Extraction
```bash
extract <file>        # Extract any archive type (.tar.gz, .zip, etc.)
```

### File Operations
```bash
backup <file>         # Quick backup with timestamp
ff <pattern>          # Find files by name
find-dir <pattern>    # Find directories by name
filesize <file>       # Get human-readable file size
```

### Development
```bash
serve [port]          # Start HTTP server (default: 8000)
weather [location]    # Get weather forecast
note [text]           # Quick note taking
```

### Docker & Git Cleanup
```bash
docker-cleanup        # Remove stopped containers, unused images/volumes
git-cleanup           # Remove merged branches
```

### Process Management
```bash
killproc <name>       # Find and kill process by name
```

## Environment Variables

### Kubernetes Shortcuts
```bash
$do      # --dry-run=client -oyaml
$now     # --force --grace-period 0
$dry     # --dry-run=client -o yaml
```

Usage example:
```bash
kubectl run nginx --image=nginx $do > nginx-pod.yaml
kubectl delete pod nginx $now
```

## Starship Prompt Features

Your prompt shows:

- **Username & hostname** (in SSH)
- **Current directory** (truncated to git repo)
- **Git branch & status**
  - `+4` = staged files
  - `~1` = modified files
  - `?1` = untracked files
  - `✓` = up to date with remote
- **Kubernetes context & namespace** (⎈)
- **Docker context** (🐳)
- **Terraform workspace** (TF:)
- **Command duration** (for slow commands)
- **Time** (24-hour format)
- **Exit status** (✓ or ✗)

### Kubernetes Context Aliases

In your Starship config, K8s contexts are aliased:
- `*pangarabbit*` → `pgr`
- `*infra*` → `dev`
- `*nonprod*` → `test`
- `*prod*` → `prod` (red warning)

## Customization

### Add Your Own Aliases

Edit `~/.aliases`:
```bash
vi ~/.aliases
# Add your aliases
szsh  # Reload
```

### Add Your Own Functions

Edit `~/.functions`:
```bash
vi ~/.functions
# Add your functions
szsh  # Reload
```

### Modify Starship Prompt

Edit `~/.config/starship.toml`:
```bash
vi ~/.config/starship.toml
# Changes take effect immediately in new prompts
```

## Zsh Features Enabled

- ✅ **Auto-completion** - Press Tab for command completion
- ✅ **History search** - Start typing and press ↑ for history
- ✅ **Incremental history** - Commands saved immediately
- ✅ **No duplicate history** - Duplicates automatically removed
- ✅ **Inline comments** - Use `#` in interactive shell
- ✅ **Unique PATH** - Prevents duplicate entries

## Troubleshooting

### Prompt Not Showing Correctly

```bash
# Check if Starship is installed
which starship

# Test Starship manually
starship prompt

# Reload config
szsh
```

### Aliases Not Working

```bash
# Check if aliases are loaded
alias | grep kubectl

# Reload config
szsh

# Check if .aliases exists
ls -la ~/.aliases
```

### Functions Not Available

```bash
# Check if functions are loaded
type mkcd

# Reload config
szsh

# Check if .functions exists
ls -la ~/.functions
```

## History Configuration

- **Location**: `~/.zsh_history`
- **Size**: 10,000 entries
- **Append mode**: Incremental (immediate save)
- **Duplicates**: Automatically removed
- **Ignored patterns**: `kubectl create secret*`, `export DOPPLER_TOKEN*`

## Performance

The configuration is optimized for remote development:
- Starship timeout: 100ms scan, 3000ms command
- No symlink following (better for network filesystems)
- Kubernetes detection only when files present
- Docker context only shown with Docker files

## Updating Configuration

To sync with your local config changes:

```bash
# From your local machine:
scp ~/.config/starship.toml pangarabbit.coder:~/.config/starship.toml
scp ~/.aliases pangarabbit.coder:~/.aliases
scp ~/.functions pangarabbit.coder:~/.functions
scp ~/.exports pangarabbit.coder:~/.exports

# Then on remote:
szsh
```

## Useful Tips

### Quick Kubernetes Context Switch

```bash
kctx <context-name>
```

### Quick Namespace Switch

```bash
kns <namespace>
```

### Generate Kubernetes YAML

```bash
k run pod-name --image=nginx $do > pod.yaml
k create deploy nginx --image=nginx $dry > deploy.yaml
```

### Start Local Web Server

```bash
serve           # Port 8000
serve 3000      # Custom port
```

### Clean Up Docker

```bash
docker-cleanup  # Remove all unused resources
```

## Integration with Zed

When you open a terminal in Zed (connected to pangarabbit.coder):
- ✅ Zsh is automatically used
- ✅ Starship prompt is active
- ✅ All aliases and functions available
- ✅ Full color support

## Next Steps

1. **Test aliases**: Try `k get pods` or `gs` in a git repo
2. **Customize**: Add your own aliases to `~/.aliases`
3. **Explore functions**: Try `mkcd test-dir` or `weather`
4. **Configure Starship**: Modify `~/.config/starship.toml` for your taste

---

**Documentation saved:** February 8, 2025  
**Ready to use** ✓