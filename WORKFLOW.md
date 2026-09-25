# JANISSARY — Port Workflow Tracker

## STATUS: PHASE 2 — IN PROGRESS
## NEXT: P2.3 — Admin panel probe
## LAST COMPLETED: P2.2 — WebSocket scanner (178 tests pass)

Last updated: 2026-09-25
Project root: C:\Users\M5 E60\janissary-project\janissary

---

## How to resume after losing context

From PowerShell, in the project root:

    Get-Content WORKFLOW.md -TotalCount 20

Or, to jump straight to the current step:

    Select-String -Path WORKFLOW.md -Pattern "## Current step" -Context 0,30

From VS Code: open WORKFLOW.md. The STATUS / NEXT / LAST COMPLETED
lines at the top tell you exactly where we are. Copy the Current Step
section into the chat and continue.

---

## Rules of engagement

1. One command at a time. Wait for output before issuing the next.
2. Never batch PowerShell commands — each is reviewed before the next.
3. Update this file at the end of every completed step.
4. If a command fails, stop and report the error before proceeding.

---

## Phase 0 — Green baseline

Goal: janissary scan finds a real SQLi on a mock server.

- [x] P0.1 Fix scanner.py indentation bug
- [x] P0.2 Nest payload loop inside the params loop
- [x] P0.3 Integration test for scanner (mock HTTP, one SQL error)
- [x] P0.4 Prototype not on disk, no-op

## Phase 1 — High-value subsystems — COMPLETE

- [x] P1.1a Credential scanner engine + CLI
- [x] P1.1b Git history walker (--scan-git + path validation)
- [x] P1.2 WAF detector + adaptive pacer
- [x] P1.3 XML-RPC multicall harness
- [x] P1.4 Platform fingerprint

## Phase 2 — Medium-value subsystems

- [x] P2.1 GraphQL fuzzer
- [x] P2.2 WebSocket scanner
- [ ] P2.3 Admin panel probe

## Phase 3 — Low-value / risky subsystems

- [ ] P3.1 SQLi UNION extractor (gated behind --attack-confirm)
- [ ] P3.2 Nuclei runner (expose NucleiRunner, drop stub)
- [ ] P3.3 Agent / FindingStore / PlatformKB

---

## P2.2 — WebSocket scanner (DONE)

Delivered:

- `src/janissary/integrations/websocket.py` — async-first WebSocket
  recon harness.
  - `WebSocketProfile` / `WebSocketFinding` dataclasses, `to_dict()`
    for JSON export.
  - `is_plaintext(url)` — flags `ws://` against non-loopback hosts.
  - `scan(url, ...)` — async entry point. Runs a baseline connect,
    then an echo probe (sends a payload, checks whether it comes back
    verbatim), then a second connect with an evil Origin header to
    detect cross-site WebSocket hijacking.
  - `scan_sync(url, ...)` — `asyncio.run` wrapper for sync callers.
  - Pins `proxy=None` on connect so environment proxy settings never
    leak into a scanner run; uses websockets 17.x's dedicated
    `user_agent_header` parameter rather than injecting a duplicate
    header via `additional_headers`.
- `src/janissary/integrations/__init__.py` — exports
  `WebSocketProfile`, `WebSocketFinding`, `is_plaintext`,
  `profile_to_json`, plus `websocket_scan` / `websocket_scan_sync`
  aliases (the bare names `scan` / `scan_sync` are deliberately not
  re-exported to avoid shadowing the GraphQL/XML-RPC namespace).
- `src/janissary/cli.py` — new `janissary ws <url>` subcommand with
  `--timeout`, `--origin`, `--evil-origin`, `--payload`, `--export`,
  `--quiet`.
- `tests/unit/test_websocket.py` — 13 tests. Spins up real
  in-process `websockets.serve` instances on ephemeral localhost
  ports: baseline handshake, echo detection, silent-server path,
  origin-not-checked finding, origin-enforced (via
  `process_request`) no-finding, unreachable-host error path, and
  a threaded sync-wrapper test.

Suite: 178 tests passing. Ruff clean.

---

## P2.1 — GraphQL fuzzer (DONE)

Delivered:

- `src/janissary/integrations/graphql.py` — full GraphQL harness.
  - `GraphQLClient` — JSON POST wrapper with `query`, `batch`, and
    `post_raw`.
  - Query builders: `build_nested_query` (depth), `build_alias_query`
    (alias amplification), `build_argument_query` (payload injection),
    plus a GraphQL-literal serializer that escapes quotes, backslashes,
    newlines, and null bytes.
  - `detect()` — probes candidate endpoints (`/graphql`, `/api/graphql`,
    `/v1/graphql`, `/query`, `/gql`, or an explicit path), runs the
    minimal `__typename` probe, then introspection, then batching,
    then suggestion support. Returns a `GraphQLProfile`.
  - `enumerate_fields()` — recovers field names from "Did you mean"
    suggestions, iterated over one or more rounds.
  - `depth_probe()` — exponential + binary search for the deepest
    accepted nesting, with refusal message capture.
  - `alias_probe()` — same strategy for the maximum accepted alias
    count in a single query.
  - `fuzz_arguments()` — runs `ARG_PAYLOADS` (SQLi, NoSQL, SSRF,
    traversal, null byte, deep object) into a given field/argument.
- `src/janissary/integrations/__init__.py` — new exports; XML-RPC
  `detect`/`resolve_endpoint` aliased as `xmlrpc_detect` /
  `xmlrpc_resolve_endpoint` to avoid collision with the GraphQL
  versions.
- `src/janissary/cli.py` — new `janissary graphql <url>` subcommand
  with `--endpoint-path`, `--timeout`, `--proxy`, `--enumerate-fields`,
  `--depth-probe`, `--alias-probe`, `--fuzz-args FIELD:ARG`, `--export`,
  `--quiet`.
- `tests/unit/test_graphql.py` — 25 tests: builders, literal escaping,
  response parsing (success, error, non-JSON, transport error, batch),
  endpoint resolution, detection (introspection on/off, HTTP error),
  field enumeration (with and without suggestions), stateful depth and
  alias probes, and argument fuzzing.

Suite: 165 tests passing. Ruff clean.

CLI-triggered fuzzing is deliberately conservative: argument fuzzing
is off by default and must be opted in with `--fuzz-args`.

---

## P1.4 — Platform fingerprint (DONE)

Delivered:

- `src/janissary/recon/fingerprint.py` — `Fingerprinter` class and
  `fingerprint()` entry point. Collects `Server`, `X-Powered-By`,
  `Set-Cookie` names, `<title>`, `<meta name="generator">`, favicon
  SHA-256 prefix, and probes common CMS paths (WordPress, Drupal,
  Joomla, Magento, Ghost, TYPO3). CMS voting combines cookie
  signatures, generator meta, and path hits. Returns a
  `Fingerprint` dataclass with `to_dict()` for JSON export.
- `src/janissary/recon/__init__.py` — exports `Fingerprint`,
  `Fingerprinter`, `fingerprint`.
- `src/janissary/cli.py` — `janissary fingerprint <url>` is now a
  real command. New flags: `--timeout`, `--proxy`, `--no-cms-paths`,
  `--no-favicon`, `--export`, `--quiet`.
- `tests/unit/test_fingerprint.py` — 15 tests.

Suite: 140 tests passing. Ruff clean.

---

## P1.3 — XML-RPC multicall harness (DONE)

See prior revision of this file. CLI wiring for the harness is still
deferred; when added, it will be a `janissary xmlrpc` subcommand.

---

## P1.2 — WAF detector + adaptive pacer (DONE)

See prior revision of this file.

---

## Current step

P2.3 — Admin panel probe.

Not yet started. Design notes to consider:

- New module `src/janissary/recon/admin.py` (recon is the natural
  home; it is a discovery step, not a protocol client).
- What to probe: well-known admin paths per platform (WordPress
  /wp-admin/, Drupal /user/login, Joomla /administrator/, Magento
  /admin/, Tomcat /manager/html, Jenkins /manage, Grafana /login,
  Kubernetes /api/v1/namespaces, etc.). Reuse the CMS tables from
  `recon/fingerprint.py` where possible.
- Report, per path: status code, redirect target, presence of a
  login form (regex on `<form>` with a password input), and whether
  the response leaks a version string.
- Never submit credentials, never attempt default logins — just
  identity and version disclosure.
- A `janissary admin <url>` CLI subcommand with `--wordlist` (custom
  path list), `--timeout`, `--proxy`, `--export`, `--quiet`.
- Tests in `tests/unit/test_admin.py`, mocked-session pattern.

---

## Git status note (deferred)

This session produced a large batch of new/modified files that are
not yet committed. When ready to publish:

    git status
    git add src tests WORKFLOW.md
    git commit -m "P1.2-P1.4: recon, integrations, fingerprinting (140 tests)"
    git push

Also decide what to do with the stale `.bak` files under
`src/janissary/credentials/` and `tests/unit/` — either delete them
or add a `.bak` rule to `.gitignore` before committing.
