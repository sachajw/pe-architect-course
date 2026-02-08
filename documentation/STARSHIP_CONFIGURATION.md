# Starship Prompt Configuration Guide

**Date:** February 8, 2025  
**Environment:** pe architecture (pangarabbit.coder)  
**Status:** ✅ Fully Configured

## Overview

Starship is a minimal, fast, and customizable prompt for any shell. It's configured on your remote development environment to provide rich contextual information about your current directory, git status, Kubernetes context, and more.

## Installation Location

- **Binary:** `/usr/local/bin/starship`
- **Version:** 1.24.2
- **Config File:** `~/.config/starship.toml`

## Features Enabled

### What Your Prompt Shows

```
root at pangarabbit …/pe-coder-aidp main +4/- [~1?1✓] ⎈ 5min-idp 📦 Docker
15:01 ➜
```

**Breaking it down:**

1. **Username** - `root` (colored orange)
2. **Hostname** - `pangarabbit` (shown in SSH sessions)
3. **Directory** - `…/pe-coder-aidp` (truncated, git-aware)
4. **Git Branch** - `main` (purple)
5. **Git Status** - `+4/-` (4 additions, deletions)
6. **Git Details** - `[~1?1✓]` (1 modified, 1 untracked, up to date)
7. **Kubernetes** - `⎈ 5min-idp` (cyan, current context)
8. **Docker** - `📦 Docker` (when Docker files present)
9. **Time** - `15:01` (24-hour format)
10. **Prompt Symbol** - `➜` (green = success, red = error)

## Configuration File

Location: `~/.config/starship.toml`

### Key Sections

#### Prompt Format
The order of modules in your prompt:
```toml
format = """
$username\
$hostname\
$kubernetes\
$docker_context\
$directory\
$git_branch\
$git_status\
$golang\
$nodejs\
$python\
$terraform\
$jobs\
$cmd_duration\
$line_break\
$character"""
```

#### Right-Side Prompt
```toml
right_format = """$time$battery$status$shell"""
```

### Important Settings

#### Performance
```toml
scan_timeout = 100         # Fast directory scanning (100ms)
command_timeout = 3000     # Command timeout (3 seconds)
follow_symlinks = false    # Better for network filesystems
```

#### Colors
```toml
[palettes.foo]
blue = '21'
mustard = '#af8700'
```

## Module Configuration

### Username Display
```toml
[username]
show_always = true                    # Always show username
format = '[$user]($style) '
style_user = "fg:#F47A26"            # Orange
style_root = "fg:#F47A26 "           # Orange (root)
```

### Directory
```toml
[directory]
truncation_length = 3                 # Show max 3 parent dirs
truncate_to_repo = true              # Truncate to git root
format = "[$path]($style)[$read_only]($read_only_style) "
style = "bg:none fg:#F47A26 bold"
home_symbol = "~"
truncation_symbol = "…/"
```

### Git Branch
```toml
[git_branch]
format = '[$symbol$branch]($style) '
symbol = ""                          # Git icon
style = "bold purple"
truncation_length = 18               # Max branch name length
```

### Git Status
```toml
[git_status]
format = '([\[$all_status$ahead_behind\]]($style))'
conflicted = "!"                     # Merge conflicts
ahead = "↑${count}"                  # Commits ahead
diverged = "↕${ahead_count}↓${behind_count}"
behind = "↓${count}"                 # Commits behind
up_to_date = "✓"
untracked = "?${count}"             # Untracked files
stashed = "*${count}"               # Stashed changes
modified = "~${count}"              # Modified files
staged = '+${count}'                # Staged changes
renamed = "→${count}"
deleted = "✗${count}"
style = "bold red"
```

### Kubernetes
```toml
[kubernetes]
symbol = "⎈ "                        # Kubernetes helm symbol
format = '[$symbol$context( @$namespace)]($style) '
style = "cyan bold"
disabled = false                     # Auto-detect when active
detect_files = ['k8s', 'kubernetes']
detect_folders = ['.kube']
```

#### Context Aliases
Your cluster contexts are aliased for cleaner display:

```toml
[[kubernetes.contexts]]
context_pattern = ".*pangarabbit.*"
context_alias = "pgr"
style = "bold cyan"

[[kubernetes.contexts]]
context_pattern = ".*infra.*"
context_alias = "dev"
style = "bold green"

[[kubernetes.contexts]]
context_pattern = ".*nonprod.*"
context_alias = "test"
style = "bold yellow"

[[kubernetes.contexts]]
context_pattern = ".*prod.*"
context_alias = "prod"
style = "bold red"                   # Red warning for production!
```

### Docker Context
```toml
[docker_context]
format = "[$symbol$context]($style) "
symbol = "🐳 "
only_with_files = true               # Only show when Docker files present
detect_files = ["docker-compose.yml", "docker-compose.yaml", "Dockerfile"]
style = "blue bold"
```

### Command Duration
```toml
[cmd_duration]
min_time = 5_000                     # Only show for commands > 5 seconds
format = "⏱ [$duration]($style) "
style = "bold yellow"
```

### Character (Prompt Symbol)
```toml
[character]
success_symbol = "[➜](bold green) "  # Success
error_symbol = "[✗](bold red) "      # Error
vicmd_symbol = "[←](bold green)"     # Vi mode
```

### Language Versions

Starship shows versions for detected languages:

- **Go** - When `go.mod` present
- **Node.js** - When `package.json` present
- **Python** - When `.python-version`, `Pipfile`, etc. present
- **Rust** - When `Cargo.toml` present

### Terraform
```toml
[terraform]
format = '[$symbol$workspace]($style) '
symbol = "TF:"
detect_folders = [".terraform"]
style = "bold_105"
```

## Customization

### Edit Configuration

```bash
# Edit Starship config
vi ~/.config/starship.toml

# Changes take effect immediately in new prompts
# No need to reload shell
```

### Test Configuration

```bash
# Test current prompt
starship prompt

# Validate config
starship config | head -20
```

### Common Customizations

#### Change Prompt Character
```toml
[character]
success_symbol = "[→](bold green) "
error_symbol = "[×](bold red) "
```

#### Disable a Module
```toml
[docker_context]
disabled = true
```

#### Add Custom Module
```toml
[custom.my_module]
command = "echo 'custom'"
when = "test -f .myfile"
format = "[$output]($style) "
style = "bold blue"
```

#### Change Time Format
```toml
[time]
time_format = "%I:%M %p"            # 12-hour format
# or
time_format = "%H:%M:%S"            # With seconds
```

## Performance Tuning

For large repositories or slow filesystems:

```toml
# Increase timeouts
scan_timeout = 200
command_timeout = 5000

# Disable expensive modules
[git_metrics]
disabled = true

# Reduce git status details
[git_status]
disabled = true
```

## Troubleshooting

### Prompt Not Showing Correctly

**Check if Starship is initialized:**
```bash
# Should see starship in shell config
cat ~/.zshrc | grep starship

# Should show: eval "$(starship init zsh)"
```

**Reload shell:**
```bash
source ~/.zshrc
# or
szsh
```

### Icons/Symbols Not Showing

**Issue:** Missing Nerd Font

**Solution:** Your terminal needs a Nerd Font installed. Common options:
- FiraCode Nerd Font
- JetBrains Mono Nerd Font
- Hack Nerd Font

In Zed, this is configured in your local settings.

### Slow Prompt

**Check which modules are slow:**
```bash
starship timings
```

**Disable slow modules** in `~/.config/starship.toml`

### Kubernetes Context Not Showing

**Check if kubectl is available:**
```bash
which kubectl
kubectl cluster-info
```

**Check kubernetes module:**
```bash
# Should not be disabled
grep -A 5 "\[kubernetes\]" ~/.config/starship.toml
```

### Git Information Not Showing

**Ensure you're in a git repository:**
```bash
git status
```

**Check git modules enabled:**
```bash
grep -A 5 "\[git_" ~/.config/starship.toml
```

## Integration with Zsh

Starship is initialized in your `~/.zshrc`:

```bash
#### starship start ####
eval "$(starship init zsh)"
#### starship end ####
```

This happens **after** all other shell setup, ensuring environment variables and paths are set correctly.

## Updating Configuration

### From Local Machine

If you update your local Starship config and want to sync:

```bash
# Copy to remote
scp ~/.config/starship.toml pangarabbit.coder:~/.config/starship.toml
```

### Backup Current Config

```bash
# Create backup
cp ~/.config/starship.toml ~/.config/starship.toml.backup

# Restore if needed
cp ~/.config/starship.toml.backup ~/.config/starship.toml
```

## Advanced Features

### Conditional Modules

Only show modules when certain conditions are met:

```toml
[custom.k3s]
command = 'kubectl version --client --short'
when = '''test -f /etc/rancher/k3s/k3s.yaml'''
format = '[k3s $output]($style) '
style = 'bold cyan'
```

### Environment Variables in Prompt

```toml
[env_var.ENVIRONMENT]
symbol = "🌍 "
variable = "ENVIRONMENT"
format = "[$symbol$env_value]($style) "
style = "bold blue"
```

### Shell Detection

Show which shell you're using:

```toml
[shell]
disabled = false
bash_indicator = "bash"
zsh_indicator = "zsh"
format = "[$indicator]($style) "
style = "cyan bold"
```

## Resources

- **Official Docs:** https://starship.rs/
- **Config Schema:** https://starship.rs/config/
- **Presets:** https://starship.rs/presets/
- **GitHub:** https://github.com/starship/starship

## Quick Reference

```bash
# View config
cat ~/.config/starship.toml

# Edit config
vi ~/.config/starship.toml

# Test prompt
starship prompt

# Check version
starship --version

# Show timing info
starship timings

# Validate config
starship config
```

---

**Configuration File:** `~/.config/starship.toml`  
**Documentation:** https://starship.rs/  
**Last Updated:** February 8, 2025 ✓