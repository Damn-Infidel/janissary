# JANISSARY — Port Workflow Tracker

## STATUS: PHASE 1 COMPLETE — PHASE 2 READY
## NEXT: P2.1 — GraphQL fuzzer
## LAST COMPLETED: P1.4 — Platform fingerprint (140 tests pass)

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

- [ ] P2.1 GraphQL fuzzer
- [ ] P2.2 WebSocket scanner
- [ ] P2.3 Admin panel probe

## Phase 3 — Low-value / risky subsystems

- [ ] P3.1 SQLi UNION extractor (gated behind --attack-confirm)
- [ ] P3.2 Nuclei runner (expose NucleiRunner, drop stub)
- [ ] P3.3 Agent / FindingStore / PlatformKB

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

P2.1 — GraphQL fuzzer.

Not yet started. Design notes to consider:

- New module: `src/janissary/protocols/graphql.py` (create the
  `protocols` package) or `src/janissary/integrations/graphql.py`.
  Given the XML-RPC client lives under `integrations`, keep GraphQL
  there for symmetry unless it needs the same status as `detection`.
- Surface to cover: introspection query, `__schema`/`__type` probes,
  field-suggestion enumeration (server errors leak field names),
  depth-bomb, alias amplification (many aliases in one request),
  batched-query abuse, and injection-into-arguments probing.
- Reuse the existing `DifferentialAnalyzer` from `detection` for
  response comparison rather than reimplementing baseline logic.
- Reuse `AdaptivePacer` and `WAFDetector` from `recon` at the call
  site, not inside the GraphQL module.
- Add a `janissary graphql <url>` CLI subcommand with
  `--endpoint-path` (default `/graphql`), `--introspect`,
  `--field-enum`, and `--export`.
- Tests in `tests/unit/test_graphql.py`, mocked-session pattern.

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
