#!/usr/bin/env python3
"""
MCP Configuration Manager

Manage and generate AI CLI configurations from master-config.json.
This is the single source of truth for all MCP server configurations.

Usage:
    python generate-configs.py              # Generate all configs from master
    python generate-configs.py --sync       # Sync and generate (same as above)
    python generate-configs.py --list       # List all configured servers
"""

import json
import sys
from pathlib import Path


def load_master_config() -> dict:
    """Load master configuration."""
    config_path = Path.home() / ".ccs" / "shared" / "master-config.json"
    with open(config_path, "r") as f:
        return json.load(f)


def generate_claude_code_config(master_config: dict) -> dict:
    """
    Generate Claude Code format configuration.
    
    Format:
    {
      "mcpServers": {
        "server-name": {
          "type": "stdio",
          "command": "cmd",
          "args": ["arg1", "arg2"],
          "env": {"KEY": "value"}
        }
      }
    }
    """
    config = {
        "$schema": "https://json.schemastore.org/claude-code-settings.json",
        "mcpServers": {}
    }
    
    for server in master_config["mcpServers"]:
        # Skip servers without a command (but allow HTTP-based servers)
        if "command" not in server or not server["command"]:
            # HTTP-based servers use serverUrl instead of command
            if "serverUrl" in server:
                continue
            print(f"⚠️ Warning: Skipping server '{server.get('name', 'unknown')}' because it has no command.")
            continue

        server_config = {
            "type": "stdio",
            "command": server["command"][0]
        }

        # Only add args if non-empty
        args = server["command"][1:]
        if args:
            server_config["args"] = args

        # Only add env if non-empty
        if server["env"]:
            server_config["env"] = server["env"]

        config["mcpServers"][server["name"]] = server_config

    return config


def generate_opencode_config(master_config: dict) -> dict:
    """
    Generate OpenCode format configuration.
    
    Format:
    {
      "mcp": {
        "server-name": {
          "type": "local",
          "command": ["cmd", "arg1", "arg2"],
          "enabled": true,
          "environment": {"KEY": "value"}
        }
      }
    }
    """
    config = {
        "$schema": "https://opencode.ai/config.json",
        "tools": master_config.get("tools", {"write": True, "bash": True}),
        "permission": master_config.get("permission", {"edit": "ask"}),
        "mcp": {}
    }
    
    for server in master_config["mcpServers"]:
        if "command" not in server or not server["command"]:
            continue
            
        opencode_server = {
            "type": "local",
            "command": server["command"],
            "enabled": True
        }
        
        # Only add environment if not empty
        if server["env"]:
            opencode_server["environment"] = server["env"]
        
        config["mcp"][server["name"]] = opencode_server
    
    return config


def generate_warp_config(master_config: dict) -> dict:
    """
    Generate Warp format configuration (flat structure).
    
    Format:
    {
      "server-name": {
        "command": "cmd",
        "args": ["arg1", "arg2"],
        "env": {"KEY": "value"}
      }
    }
    """
    config = {}
    
    for server in master_config["mcpServers"]:
        if "command" not in server or not server["command"]:
            continue

        server_config = {
            "command": server["command"][0]
        }

        # Only add args if non-empty
        args = server["command"][1:]
        if args:
            server_config["args"] = args

        # Only add env if non-empty
        if server["env"]:
            server_config["env"] = server["env"]

        config[server["name"]] = server_config

    return config


def save_config(config: dict, path: Path) -> None:
    """Save configuration to file."""
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def merge_mcp_servers(mcp_servers: dict, path: Path) -> None:
    """
    Merge MCP servers into an existing config file.
    Only updates the root-level 'mcpServers' key, preserving all other data.
    """
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config or create empty dict
    existing_config = {}
    if path.exists():
        try:
            with open(path, "r") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing_config = {}

    # Update only the root-level mcpServers
    existing_config["mcpServers"] = mcp_servers

    with open(path, "w") as f:
        json.dump(existing_config, f, indent=2)


def list_servers(master_config: dict) -> None:
    """List all configured MCP servers."""
    servers = master_config["mcpServers"]
    print(f"\n📋 Configured MCP Servers ({len(servers)}):\n")
    
    for i, server in enumerate(servers, 1):
        name = server.get('name', 'unknown')
        command = ' '.join(server.get('command', [])) or "NO COMMAND"
        print(f"{i:2}. {name}")
        print(f"    Command: {command}")
        if server.get('env'):
            print(f"    Environment: {len(server['env'])} variable(s)")
        print()


def sync_configs(master_config: dict) -> None:
    """Generate all configs from master configuration."""
    print("🔄 Generating AI CLI configurations...")
    print()
    
    print(f"📋 Loaded master config with {len(master_config['mcpServers'])} servers")
    print()
    
    # Generate configs
    claude_code_config = generate_claude_code_config(master_config)
    opencode_config = generate_opencode_config(master_config)
    warp_config = generate_warp_config(master_config)
    
    # Save configs (full overwrite)
    home = Path.home()
    configs = [
        (claude_code_config, home / ".ccs" / "shared" / "settings.json", "CCS Shared"),
        (claude_code_config, home / ".claude" / "settings.json", "Claude Code"),
        (opencode_config, home / ".opencode" / "opencode.json", "OpenCode"),
        (warp_config, home / ".warp" / "mcp_config.json", "Warp"),
    ]

    for config, path, name in configs:
        save_config(config, path)
        print(f"✅ {name}: {path}")

    # Merge MCP servers into main Claude config (preserves other data)
    main_claude_path = home / ".claude.json"
    merge_mcp_servers(claude_code_config["mcpServers"], main_claude_path)
    print(f"✅ Claude Code Main (merged): {main_claude_path}")

    # Merge MCP servers into CCS .claude config (preserves other data)
    # This is the config file that Claude Code actually reads from
    ccs_claude_path = home / ".ccs" / ".claude" / ".claude.json"
    merge_mcp_servers(claude_code_config["mcpServers"], ccs_claude_path)
    print(f"✅ CCS Claude Config (merged): {ccs_claude_path}")

    # Merge MCP servers into instance config (preserves other data)
    instance_path = home / ".ccs" / "instances" / "claude" / ".claude.json"
    merge_mcp_servers(claude_code_config["mcpServers"], instance_path)
    print(f"✅ Claude Code Instance (merged): {instance_path}")
    
    print()
    print("🎉 All configs generated successfully!")
    print()
    print("Next steps:")
    print("  - Restart Claude Code / OpenCode / Warp to load new configs")
    print("  - Verify with: claude mcp list / opencode mcp list")


def show_usage() -> None:
    """Show usage information."""
    print("""
MCP Configuration Manager

Usage:
    python generate-configs.py              Generate all configs
    python generate-configs.py --sync       Sync and generate (same as above)
    python generate-configs.py --list       List all configured servers
    python generate-configs.py --help       Show this help message

Master config location: ~/.ccs/shared/master-config.json

To add or modify servers, edit the master-config.json file directly.
""")


def main():
    """Main function."""
    args = sys.argv[1:]
    
    # Parse arguments
    if "--help" in args or "-h" in args:
        show_usage()
        return 0
    
    # Load master config
    try:
        master_config = load_master_config()
    except FileNotFoundError:
        print("❌ Error: master-config.json not found at ~/.ccs/shared/")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in master-config.json: {e}")
        return 1
    
    # Handle commands
    if "--list" in args:
        list_servers(master_config)
    else:
        # Default action or --sync
        sync_configs(master_config)

    return 0


if __name__ == "__main__":
    main()
