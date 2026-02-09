# Shell Configuration Guide

This guide documents the shell configuration setup for the development environment, including topgrade, Oh-My-Zsh, fzf, and various shell enhancements.

## Overview

The shell environment uses:
- **Zsh** as the primary shell
- **Starship** for the prompt
- **Oh-My-Zsh** for plugins and enhancements
- **fzf** for fuzzy finding
- **topgrade** for system updates

## Topgrade Configuration

### Location
- Config: `~/.config/topgrade.toml`

### Key Settings

**Disabled Components** (not installed or managed elsewhere):
```toml
disable = ["vscode_insiders", "brew_formula", "brew_cask", "bun", "certbot", "containers", "uv", "vim", "vscode", "flatpak"]
```

**Ignored Failures** (by design):
```toml
ignore_failures = ["helm"]  # No repositories configured
```

**Behavior**:
- `assume_yes = true` - No confirmations
- `no_retry = true` - Skip retry prompts
- `cleanup = true` - Clean temporary files
- `show_skipped = true` - Show why steps are skipped

**NPM/Yarn**:
```toml
[npm]
use_sudo = true  # Required on Ubuntu systems

[yarn]
use_sudo = true  # Required on Ubuntu systems
```

### Environment Variables

To run topgrade as root without prompts:
```bash
export TOPGRADE_RUN_IN_ROOT=1
```

This is set in `~/.exports`.

### Usage
```bash
topgrade        # Full system update
topgrade -y     # Skip confirmations (redundant with config)
topgrade --dry-run  # Preview what would be updated
```

## Oh-My-Zsh Configuration

### Installation Location
`~/.oh-my-zsh/`

### Configuration
Settings are in `~/.zshrc`, not a separate Oh-My-Zsh config file.

### Enabled Plugins

```bash
plugins=(
  git                    # Git aliases and completions
  docker                 # Docker completions and aliases
  docker-compose         # Docker Compose completions
  kubectl                # Kubectl completions and aliases
  helm                   # Helm completions
  command-not-found      # Suggest package installation for missing commands
  colored-man-pages      # Colorize man pages
  sudo                   # Press ESC twice to prefix command with sudo
  history                # History aliases (h, hsi, hstr)
  cp                     # cpv - verbose copy with progress
)
```

### Theme
```bash
ZSH_THEME=""  # Disabled - using Starship instead
```

### Updates
```bash
zstyle ':omz:update' mode disabled  # Let topgrade handle updates
```

### Plugin Features

**Git Plugin**:
- `gst` ??? `git status`
- `gco` ??? `git checkout`
- `glog` ??? pretty git log
- `gp` ??? `git push`
- Tab completion for branches/remotes

**Docker Plugin**:
- `dps` ??? `docker ps`
- `dex` ??? `docker exec -it`
- `dlog` ??? `docker logs`
- Tab completion for containers/images

**Kubectl Plugin**:
- `k` ??? `kubectl`
- `kgp` ??? `kubectl get pods`
- `kdp` ??? `kubectl describe pod`
- Tab completion for resources

**Helm Plugin**:
- Tab completion for releases/charts/flags

**command-not-found**:
- Suggests package installation when command not found
- Example: Type `htop` ??? suggests `sudo apt install htop`

**sudo Plugin**:
- Press `ESC` twice to prepend `sudo` to current command

**colored-man-pages**:
- Syntax highlighting for `man` pages

**history Plugin**:
- `h` ??? show history
- `hsi` ??? search history interactively

**cp Plugin**:
- `cpv` ??? verbose copy with progress bar

### Alias Precedence

Custom aliases in `~/.aliases` override Oh-My-Zsh aliases since they're loaded last:

```bash
source $ZSH/oh-my-zsh.sh           # Oh-My-Zsh loads first
...
[[ -r ~/.aliases ]] && source ~/.aliases  # Custom aliases override
```

## fzf (Fuzzy Finder)

### Installation
```bash
apt install -y fzf
```

### Configuration
Located in `~/.zshrc`:
```bash
source /usr/share/doc/fzf/examples/key-bindings.zsh
source /usr/share/doc/fzf/examples/completion.zsh
```

### Key Bindings

- **Ctrl+R** - Fuzzy search command history
- **Ctrl+T** - Fuzzy search files in current directory
- **Alt+C** - Fuzzy search and cd into directories

### Completion
Use `**<TAB>` for fuzzy completion:
```bash
vim **<TAB>      # Fuzzy find files
cd **<TAB>       # Fuzzy find directories
kill -9 **<TAB>  # Fuzzy find processes
```

## Shell Startup Flow

The `~/.zshrc` loads components in this order:

1. **Zsh settings** (options, completions)
2. **Environment variables** (`~/.exports`)
3. **Functions** (`~/.functions`)
4. **Aliases** (`~/.aliases`)
5. **Oh-My-Zsh** (plugins, completions)
6. **Starship** (prompt)
7. **fzf** (fuzzy finder integration)
8. **Custom startup scripts** (e.g., Capacitor auto-start)

This order ensures:
- Environment variables are available to all subsequent components
- Custom aliases override Oh-My-Zsh defaults
- Starship renders after Oh-My-Zsh to avoid conflicts

## Starship vs Oh-My-Zsh Themes

**Starship**:
- Cross-shell prompt (Zsh, Bash, Fish, PowerShell)
- Fast (written in Rust)
- Just handles the prompt

**Oh-My-Zsh Themes**:
- Zsh-only
- Part of larger framework
- Can be slower

**Current Setup**: Using Starship for prompt + Oh-My-Zsh for plugins (best of both worlds).

## Troubleshooting

### Topgrade Issues

**"brew" is an unknown variant**:
- Fixed by using `brew_formula` and `brew_cask` instead
- Config automatically updated

**VSCode extensions failing**:
- VSCode not installed
- Disabled via `disable = ["vscode", "vscode_insiders"]`

**Root prompt**:
- Set `TOPGRADE_RUN_IN_ROOT=1` to skip

### Oh-My-Zsh Issues

**Slow startup**:
- Too many plugins enabled
- Disable unused plugins in `~/.zshrc`

**Alias conflicts**:
- Custom aliases in `~/.aliases` take precedence
- Check with `alias <name>` to see current value

**Theme interfering with Starship**:
- Ensure `ZSH_THEME=""` in `~/.zshrc`

### fzf Issues

**Key bindings not working**:
- Reload shell: `source ~/.zshrc`
- Check bindings with `bindkey | grep fzf`

**No files shown with Ctrl+T**:
- fzf respects `.gitignore` by default
- Use `FZF_CTRL_T_COMMAND` to customize

## Related Documentation

- [STARSHIP_CONFIGURATION.md](./STARSHIP_CONFIGURATION.md) - Starship prompt setup
- [ZSH_REMOTE_SETUP.md](./ZSH_REMOTE_SETUP.md) - Remote Zsh configuration
- [SESSION_STATE.md](./SESSION_STATE.md) - Session persistence
