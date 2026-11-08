# agent-utils-swarm

Thin Python client for the **agent_utils Swarm** server - stateful coordination for AI agents over MCP: memory, locks, task board, pub/sub, idempotency and webhook inboxes.

This is a client for a hosted commercial service ([agent-utils.ai](https://agent-utils.ai)), not the service itself. Zero dependencies (standard library only). Install name `agent-utils-swarm`; import `agent_utils.swarm` (a namespace package).

## Install

```bash
pip install agent-utils-swarm
```

## Quickstart

```python
import json, os
from agent_utils.swarm import AgentUtilsSwarm

# Any secret works as a token; the first call auto-provisions a free trial.
swarm = AgentUtilsSwarm(token=os.environ["AGENT_UTILS_TOKEN"])

swarm.put_memory("project", "status", json.dumps({"phase": "review"}))

# Hand work out through the task board; any agent can claim it atomically.
swarm.create_task(board="launch", title="Write release notes")
claimed = swarm.claim_task(board="launch", agent_name="writer")

# Tell the rest of the swarm, and wait (long-poll) for replies.
swarm.publish(topic="launch", body="release notes in progress", sender="writer")
news = swarm.read_topic(topics=["launch"], wait_seconds=20)
```

## API

**Memory** - persistent key-value memory
- `get_memory(namespace, key)`
- `put_memory(namespace, key, value_json, months?, tags?, priority?)`
- `replace_memory(namespace, key, value_json, priority?, summary?, tags_to_add?, tags_to_delete?)`
- `extend_memory_ttl(namespace, key, months)`
- `delete_memory(namespace, key)`
- `list_keys(namespace)`
- `list_namespaces()`
- `search_by_tag(tag)`
- `top_memories(namespace, n)`

**Mutex** - distributed locks
- `acquire_lock(resource_id, agent_name, ttl_seconds?, reason?)`
- `release_lock(resource_id, kill_token)`
- `extend_lock(resource_id, kill_token, additional_ttl_seconds)`
- `check_lock(resource_id)`
- `list_active_locks()`

**Task board** - shared work queue with atomic claims, leases and dependencies
- `create_task(board, title, description?, priority?, depends_on?, tags?, memory?, created_by?)`
- `list_tasks(board, status?, owner?, tag?, ready_only?, limit?)`
- `get_task(board, task_id)`
- `claim_task(board, agent_name, task_id?, tag?, lease_seconds?)`
- `complete_task(board, task_id, agent_name, result?, memory?)`
- `release_task(board, task_id, agent_name)`
- `update_task(board, task_id, ...)`
- `delete_task(board, task_id)`
- `list_boards()`
- `renew_board(board, months?)`
- `delete_board(board)`

**Pub/sub** - topics agents publish to and long-poll
- `publish(topic, body, ttl_seconds?, sender?)`
- `read_topic(topics, after?, limit?, wait_seconds?)`
- `renew_message(topic, seq, ttl_seconds?)`
- `list_topics()`
- `delete_topic(topic, delete_token)`

**Idempotency** - exactly-once operations
- `acquire_key(key, operation, agent_name)`
- `complete_key / fail_key / check_key`
- `create_operation_rule / list_operation_rules / delete_operation_rule / cleanup_operation_rules`

**Webhook inbox** - temporary webhook receivers
- `create_inbox(...)`
- `poll_inbox(...)`
- `list_inboxes()`
- `delete_inbox(...)`
- `configure_inbox_settings(...)`
- `cleanup_expired()`

**Account** (on both servers) - `get_account`, `list_api_keys`, `create_api_key`, `revoke_api_key`, `list_payments`, `settle_balance`, `submit_feature_request`, `submit_exit_feedback`, `delete_account`

- `call(name, args)` - call any tool by name

Python methods use the tool names; TypeScript methods are their camelCase forms (`claim_task` -> `claimTask`). Memory has typed parameters; the other services take keyword arguments (Python) or an args object (TypeScript) that are passed straight through as the tool's arguments.

Every response carries a `_meta` envelope with `account_status`, `op_cost`, and
`credits_remaining`. The canonical, always-current reference is the server's
[llms.txt](https://mcp.agent-utils.ai/llms.txt) (per service: `/docs/<service>`).

Endpoint: `https://mcp.agent-utils.ai/swarm` (staging: `STAGING_ENDPOINT`, `https://mcp-staging.agent-utils.ai/swarm`).

## One token, both servers

agent_utils is two MCP servers on one account: **swarm** (this one) and **extensions** (math, units). The same token works on both and draws from one credit pool. See the [agent-utils hub](https://github.com/agent-utils/agent-utils) for the full platform, and the TypeScript client [`@agent-utils-ai/swarm`](https://github.com/agent-utils/agent-utils-swarm-ts).

## Pricing

1 credit = $0.00001. Trial: 1,000 credits, no card. Activation: $5 -> 500,000-credit limit. Terms: [mcp.agent-utils.ai/legal.txt](https://mcp.agent-utils.ai/legal.txt).

## Contact

Questions, bugs or account issues: support@agent-utils.ai

## License

MIT. The hosted agent_utils service is a separate commercial product and is not open-source.
