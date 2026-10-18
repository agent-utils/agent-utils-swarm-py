# SPDX-License-Identifier: MIT
"""Thin MCP-over-HTTP client for the hosted agent_utils Swarm server.

Swarm is the stateful half of agent_utils: memory, mutex, task board, pub/sub,
idempotency and webhook inbox, all on one endpoint.

This is a client, not the service — see https://agent-utils.ai.
Zero dependencies: standard library only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

DEFAULT_ENDPOINT = "https://mcp.agent-utils.ai/swarm"
STAGING_ENDPOINT = "https://mcp-staging.agent-utils.ai/swarm"
USER_AGENT = "agent-utils-swarm-py/0.1.0"

__all__ = ["AgentUtilsSwarm", "DEFAULT_ENDPOINT", "STAGING_ENDPOINT"]


class AgentUtilsSwarm:
    """Client for the agent_utils Swarm MCP server.

    The same token works on both agent_utils servers (swarm and extensions) and
    draws from one credit pool. Any secret works as a token — the first call
    auto-provisions a free trial (no card). See https://agent-utils.ai.
    """

    def __init__(self, token: str, endpoint: str = DEFAULT_ENDPOINT) -> None:
        self._token = token
        self._endpoint = endpoint
        self._id = 0

    def call(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call any MCP tool by name and return its result."""
        self._id += 1
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": self._id,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments or {}},
            }
        ).encode()
        req = urllib.request.Request(
            self._endpoint,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                # Cloudflare rejects urllib's default User-Agent (error 1010).
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as exc:  # pragma: no cover - network error path
            raise RuntimeError(f"agent_utils HTTP {exc.code}: {exc.read().decode()}") from exc
        if isinstance(body, dict) and body.get("error"):
            raise RuntimeError(f"agent_utils: {body['error'].get('message', 'unknown error')}")
        return body.get("result") if isinstance(body, dict) else body

    # --- memory ---------------------------------------------------------------

    def get_memory(self, namespace: str, key: str) -> Any:
        return self.call("get_memory", {"namespace": namespace, "key": key})

    def put_memory(
        self,
        namespace: str,
        key: str,
        value_json: str,
        months: int | None = None,
        tags: list[str] | None = None,
        priority: int | None = None,
    ) -> Any:
        args: dict[str, Any] = {"namespace": namespace, "key": key, "value_json": value_json}
        if months is not None:
            args["months"] = months
        if tags is not None:
            args["tags"] = tags
        if priority is not None:
            args["priority"] = priority
        return self.call("put_memory", args)

    def replace_memory(
        self,
        namespace: str,
        key: str,
        value_json: str,
        priority: int | None = None,
        summary: str | None = None,
        tags_to_add: list[str] | None = None,
        tags_to_delete: list[str] | None = None,
    ) -> Any:
        """Update an existing entry.

        Errors if the key does not exist - use :meth:`put_memory` to create.
        Tags are managed explicitly; each tag operation is charged whether or
        not the tag was already present.
        """
        args: dict[str, Any] = {"namespace": namespace, "key": key, "value_json": value_json}
        if priority is not None:
            args["priority"] = priority
        if summary is not None:
            args["summary"] = summary
        if tags_to_add is not None:
            args["tags_to_add"] = tags_to_add
        if tags_to_delete is not None:
            args["tags_to_delete"] = tags_to_delete
        return self.call("replace_memory", args)

    def extend_memory_ttl(self, namespace: str, key: str, months: int) -> Any:
        """Add `months` to an existing entry's expiry.

        Bills kb-months at the current stored size. Errors if the key does not
        exist or has already expired.
        """
        return self.call(
            "extend_memory_ttl", {"namespace": namespace, "key": key, "months": months}
        )

    def delete_memory(self, namespace: str, key: str) -> Any:
        return self.call("delete_memory", {"namespace": namespace, "key": key})

    def list_keys(self, namespace: str) -> Any:
        return self.call("list_keys", {"namespace": namespace})

    def list_namespaces(self) -> Any:
        return self.call("list_namespaces", {})

    def search_by_tag(self, tag: str) -> Any:
        return self.call("search_by_tag", {"tag": tag})

    def top_memories(self, namespace: str, n: int) -> Any:
        return self.call("top_memories", {"namespace": namespace, "n": n})

    # --- mutex ----------------------------------------------------------------

    def acquire_lock(self, **kwargs: Any) -> Any:
        return self.call("acquire_lock", kwargs)

    def release_lock(self, **kwargs: Any) -> Any:
        return self.call("release_lock", kwargs)

    def extend_lock(self, **kwargs: Any) -> Any:
        return self.call("extend_lock", kwargs)

    def check_lock(self, **kwargs: Any) -> Any:
        return self.call("check_lock", kwargs)

    def list_active_locks(self, **kwargs: Any) -> Any:
        return self.call("list_active_locks", kwargs)

    # --- task board -----------------------------------------------------------

    def create_task(self, **kwargs: Any) -> Any:
        return self.call("create_task", kwargs)

    def get_task(self, **kwargs: Any) -> Any:
        return self.call("get_task", kwargs)

    def list_tasks(self, **kwargs: Any) -> Any:
        return self.call("list_tasks", kwargs)

    def update_task(self, **kwargs: Any) -> Any:
        return self.call("update_task", kwargs)

    def claim_task(self, **kwargs: Any) -> Any:
        return self.call("claim_task", kwargs)

    def complete_task(self, **kwargs: Any) -> Any:
        return self.call("complete_task", kwargs)

    def release_task(self, **kwargs: Any) -> Any:
        return self.call("release_task", kwargs)

    def delete_task(self, **kwargs: Any) -> Any:
        return self.call("delete_task", kwargs)

    def list_boards(self, **kwargs: Any) -> Any:
        return self.call("list_boards", kwargs)

    def renew_board(self, **kwargs: Any) -> Any:
        return self.call("renew_board", kwargs)

    def delete_board(self, **kwargs: Any) -> Any:
        return self.call("delete_board", kwargs)

    # --- pub/sub --------------------------------------------------------------

    def publish(self, **kwargs: Any) -> Any:
        return self.call("publish", kwargs)

    def read_topic(self, **kwargs: Any) -> Any:
        """Read messages; pass `wait_seconds` (max 20) to long-poll."""
        return self.call("read_topic", kwargs)

    def renew_message(self, **kwargs: Any) -> Any:
        return self.call("renew_message", kwargs)

    def list_topics(self, **kwargs: Any) -> Any:
        return self.call("list_topics", kwargs)

    def delete_topic(self, **kwargs: Any) -> Any:
        return self.call("delete_topic", kwargs)

    # --- idempotency ----------------------------------------------------------

    def list_operation_rules(self, **kwargs: Any) -> Any:
        return self.call("list_operation_rules", kwargs)

    def create_operation_rule(self, **kwargs: Any) -> Any:
        return self.call("create_operation_rule", kwargs)

    def delete_operation_rule(self, **kwargs: Any) -> Any:
        return self.call("delete_operation_rule", kwargs)

    def acquire_key(self, **kwargs: Any) -> Any:
        return self.call("acquire_key", kwargs)

    def complete_key(self, **kwargs: Any) -> Any:
        return self.call("complete_key", kwargs)

    def fail_key(self, **kwargs: Any) -> Any:
        return self.call("fail_key", kwargs)

    def check_key(self, **kwargs: Any) -> Any:
        return self.call("check_key", kwargs)

    def cleanup_operation_rules(self, **kwargs: Any) -> Any:
        return self.call("cleanup_operation_rules", kwargs)

    # --- webhook inbox --------------------------------------------------------

    def create_inbox(self, **kwargs: Any) -> Any:
        return self.call("create_inbox", kwargs)

    def poll_inbox(self, **kwargs: Any) -> Any:
        return self.call("poll_inbox", kwargs)

    def list_inboxes(self, **kwargs: Any) -> Any:
        return self.call("list_inboxes", kwargs)

    def delete_inbox(self, **kwargs: Any) -> Any:
        return self.call("delete_inbox", kwargs)

    def configure_inbox_settings(self, **kwargs: Any) -> Any:
        return self.call("configure_inbox_settings", kwargs)

    def cleanup_expired(self, **kwargs: Any) -> Any:
        return self.call("cleanup_expired", kwargs)

    # --- account (also on extensions) -----------------------------------------

    def get_account(self) -> Any:
        return self.call("get_account", {})

    def list_api_keys(self, **kwargs: Any) -> Any:
        return self.call("list_api_keys", kwargs)

    def create_api_key(self, **kwargs: Any) -> Any:
        return self.call("create_api_key", kwargs)

    def revoke_api_key(self, **kwargs: Any) -> Any:
        return self.call("revoke_api_key", kwargs)

    def list_payments(self, **kwargs: Any) -> Any:
        return self.call("list_payments", kwargs)

    def settle_balance(self, **kwargs: Any) -> Any:
        return self.call("settle_balance", kwargs)

    def submit_feature_request(self, **kwargs: Any) -> Any:
        return self.call("submit_feature_request", kwargs)

    def submit_exit_feedback(self, **kwargs: Any) -> Any:
        return self.call("submit_exit_feedback", kwargs)
