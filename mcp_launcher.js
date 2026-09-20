#!/usr/bin/env node
/**
 * Standalone Zalo MCP Server Launcher for Claude Code / Cursor
 */
import { autoLogin, getApi } from "./src/core/zalo-client.js";
import { MessageBuffer } from "./src/mcp/message-buffer.js";
import { ThreadFilter } from "./src/mcp/thread-filter.js";
import { loadMCPConfig, parseDuration } from "./src/mcp/mcp-config.js";
import { createMCPServer } from "./src/mcp/mcp-server.js";
import { ThreadNameCache } from "./src/mcp/thread-name-cache.js";

async function main() {
  let api = null;
  try {
    await autoLogin(false);
    api = getApi();
  } catch (e) {
    console.error("[zalo-mcp] Notice: Starting in offline/standby mode (run 'node src/index.js login' to authenticate):", e.message);
  }

  const config = loadMCPConfig();
  const maxAge = parseDuration(config.limits?.bufferMaxAge ?? "2h");
  const maxSize = config.limits?.bufferMaxSize ?? 500;
  const buffer = new MessageBuffer(maxSize, maxAge);
  const filter = new ThreadFilter(config);
  const nameCache = new ThreadNameCache();

  const server = await createMCPServer(api, buffer, filter, config, nameCache);
  console.error("[zalo-mcp] Zalo MCP Server connected via stdio transport successfully.");
}

main().catch(err => {
  console.error("[zalo-mcp] Startup error:", err);
  process.exit(1);
});
