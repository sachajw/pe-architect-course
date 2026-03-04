#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Read master config
const masterConfig = JSON.parse(fs.readFileSync(path.join(__dirname, 'master-config.json'), 'utf8'));

// Generate Claude Code format
function generateClaudeCodeConfig() {
  const config = {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    mcpServers: {}
  };

  masterConfig.mcpServers.forEach(server => {
    config.mcpServers[server.name] = {
      type: "stdio",
      command: server.command[0],
      args: server.command.slice(1),
      env: server.env
    };
  });

  return config;
}

// Generate OpenCode format
function generateOpenCodeConfig() {
  const config = {
    "$schema": "https://opencode.ai/config.json",
    tools: masterConfig.tools,
    permission: masterConfig.permission,
    mcp: {}
  };

  masterConfig.mcpServers.forEach(server => {
    config.mcp[server.name] = {
      type: "local",
      command: server.command,
      enabled: true,
      environment: server.env
    };
  });

  return config;
}

// Generate Warp format (flat structure, similar to Claude Code but no mcpServers wrapper)
function generateWarpConfig() {
  const config = {};

  masterConfig.mcpServers.forEach(server => {
    config[server.name] = {
      command: server.command[0],
      args: server.command.slice(1),
      env: server.env
    };
  });

  return config;
}

// Write configs
const claudeCodeConfig = generateClaudeCodeConfig();
const openCodeConfig = generateOpenCodeConfig();
const warpConfig = generateWarpConfig();

// Ensure directories exist
const warpDir = '/Users/tvl/.warp';
if (!fs.existsSync(warpDir)) {
  fs.mkdirSync(warpDir, { recursive: true });
}

fs.writeFileSync(
  path.join(__dirname, 'settings.json'),
  JSON.stringify(claudeCodeConfig, null, 2)
);

fs.writeFileSync(
  '/Users/tvl/.claude/settings.json',
  JSON.stringify(claudeCodeConfig, null, 2)
);

fs.writeFileSync(
  '/Users/tvl/.opencode/opencode.json',
  JSON.stringify(openCodeConfig, null, 2)
);

fs.writeFileSync(
  '/Users/tvl/.warp/mcp_config.json',
  JSON.stringify(warpConfig, null, 2)
);

console.log('✅ Generated configs for:');
console.log('   - Claude Code: ~/.claude/settings.json');
console.log('   - OpenCode: ~/.opencode/opencode.json');
console.log('   - Warp: ~/.warp/mcp_config.json');
console.log('   - Shared: ~/.ccs/shared/settings.json');
