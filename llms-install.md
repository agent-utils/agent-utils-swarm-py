# Install — instructions for an AI agent

**Nothing to clone, build, or run.** agent_utils Swarm is a *hosted* MCP server at
`https://mcp.agent-utils.ai/swarm`. Installing it means pointing your MCP client at that URL with a
Bearer token. There is no signup, no dashboard, no API-key request, and no payment card.

If you are looking for a package to launch as a local stdio server, stop — this is a remote
(Streamable HTTP) server. The npm/PyPI package below is an optional convenience client, not
the server.

## 1. Generate a token

The token *is* the account. Any sufficiently random secret works, and the first call
auto-provisions a free trial (1,000 credits).

```bash
TOKEN=sk_$(openssl rand -hex 32)
echo "$TOKEN"   # save this — losing it means losing the account and its data
```

## 2. Register the server

**Claude Code** — one command:

```bash
claude mcp add --scope user --transport http agent-utils-swarm https://mcp.agent-utils.ai/swarm \
  --header "Authorization: Bearer $TOKEN"
```

**Cline / Cursor / Windsurf** — add to the MCP settings JSON:

```json
{
  "mcpServers": {
    "agent-utils-swarm": {
      "url": "https://mcp.agent-utils.ai/swarm",
      "headers": { "Authorization": "Bearer sk_REPLACE_WITH_YOUR_TOKEN" }
    }
  }
}
```

## 3. Verify before spending anything

`tools/list` needs **no authentication**, so reachability can be confirmed before the first
billed call:

```bash
curl -s -X POST https://mcp.agent-utils.ai/swarm \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Expect 52 tools: memory, mutex, task board, pub/sub, idempotency and webhook inbox, plus the 8 shared account tools
(`get_account`, `create_api_key`, `list_api_keys`, `revoke_api_key`, `list_payments`,
`settle_balance`, `submit_feature_request`, `submit_exit_feedback`).

## 4. Confirm the account

`get_account` is free — it creates the trial account and returns its state:

```bash
curl -s -X POST https://mcp.agent-utils.ai/swarm \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_account","arguments":{}}}'
```

A successful response means installation is complete.

## Optional: the client library

```bash
pip install agent-utils-swarm
```

See `README.md` in this repo for the API.

## One token, both servers

agent_utils is two MCP servers: **swarm** (`https://mcp.agent-utils.ai/swarm` — memory, mutex,
task board, pub/sub, idempotency, webhook inbox) and **extensions**
(`https://mcp.agent-utils.ai/extensions` — math, units, currency). The same token works on
both and draws from a single credit pool. To add the other one, repeat step 2 with
`agent-utils-extensions`, `https://mcp.agent-utils.ai/extensions`, and **the same token**.

## Cost

1 credit = $0.00001. Trial: 1,000 credits, no card. A one-time $5 activation raises the limit
to 500,000 credits for the whole account. `get_account`, `settle_balance`, and
`submit_exit_feedback` are free. Terms: <https://mcp.agent-utils.ai/legal.txt>.

## Troubleshooting

- **HTTP 401** — the `Authorization` header is missing or malformed. It must be exactly
  `Bearer <token>`.
- **HTTP 403 "error code: 1010"** — Cloudflare rejected your HTTP client's default
  User-Agent (Python's `urllib` is blocked). Send any descriptive `User-Agent` header.
- **No tools listed / 404** — you are probably POSTing to the wrong path. The endpoint is
  `/swarm`, not the domain root or `/mcp`.
- **"Key already exists" on a write** — services distinguish create from update. Check the
  tool description returned by `tools/list`; it names the right tool.
- **Authoritative reference** — the server's own spec is always current:
  <https://mcp.agent-utils.ai/llms.txt>.
