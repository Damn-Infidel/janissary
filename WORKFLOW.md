# JANISSARY — Port Workflow Tracker

## STATUS: PHASE 3 — IN PROGRESS
## NEXT: P3.3 — Agent / FindingStore / PlatformKB
## LAST COMPLETED: P3.2 — Nuclei runner (257 tests pass)

Last updated: 2026-09-26
Project root: C:\Users\M5 E60\janissary-project\janissary

---

## How to resume after losing context

From PowerShell, in the project root:

    Get-Content WORKFLOW.md -TotalCount 20

Or, to jump straight to the current step:

    Select-String -Path WORKFLOW.md -Pattern "^## Current step" -Context 0,30

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

## Phase 0 — Green baseline — COMPLETE

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

## Phase 2 — Medium-value subsystems — COMPLETE

- [x] P2.1 GraphQL fuzzer
- [x] P2.2 WebSocket scanner
- [x] P2.3 Admin panel probe

## Phase 3 — Low-value / risky subsystems — IN PROGRESS

- [x] P3.1 SQLi UNION extractor (gated behind --attack-confirm)
- [x] P3.2 Nuclei runner (expose NucleiRunner, drop stub)
- [ ] P3.3 Agent / FindingStore / PlatformKB

## Legal framework — DONE

- [x] LEGAL.md + first-run acceptance gate (210 tests pass at the time)

---

## P3.1 — SQLi UNION extractor (DONE)

Delivered:

- New `src/janissary/attack/` package, separate from `detection`
  on purpose: detection identifies, attack extracts.
- `src/janissary/attack/sqli_union.py`:
    - `UnionExtractor`, `build_union_payload`, `detect_dbms`,
      `split_concat`.
    - Per-DBMS metadata queries for MySQL, PostgreSQL, MSSQL,
      Oracle, SQLite.
    - `AttackConfirmationRequired`, `UnstableTargetError`.
- Three independent safety layers: Terms-of-Use gate (fires because
  `attack` is in `legal.GATED_COMMANDS`), `--attack-confirm` flag,
  and `attack_confirm=True` at the class level.
- Hard limits: columns 1-32, max_rows <= 100, max_bytes <= 65536.
- CLI: `janissary attack sqli-union <url> --param X --columns N
  --attack-confirm`.
- `tests/unit/test_sqli_union.py` — 25 tests, payload-aware mock.

Suite: 235 tests passing. Ruff clean.

---

## Legal framework — Terms of Use + acceptance gate (DONE)

- `LEGAL.md` — supplementary Terms of Use. Clauses: authorised use,
  indemnity, limitation of liability, export control, good-faith
  research, no warranty, governing law. Apache-2.0 remains the code
  licence; LEGAL.md supplements it. Governing law: Victoria,
  Australia.
- `src/janissary/legal.py` — versioned terms text, marker helpers
  (`~/.janissary/terms-accepted.json`), `require_acceptance()`.
- `src/janissary/cli.py` — gate in `main()`. Gated commands: scan,
  fingerprint, graphql, ws, admin, attack. New `janissary terms
  {show,status,accept}` subcommand.
- `README.md` — Authorised-Use block at the top.
- `tests/unit/test_legal.py` — 19 tests.

---

## P2.3 — Admin panel probe (DONE)

- `src/janissary/recon/admin.py` — `ADMIN_PATHS` (18 platforms),
  `AdminProbe`, `probe_admin`.
- `janissary admin <url>` CLI subcommand.
- `tests/unit/test_admin.py` — 13 tests.

## P2.2 — WebSocket scanner (DONE)

- `src/janissary/integrations/websocket.py` — async `scan`, sync
  `scan_sync`, `is_plaintext`, echo probe, CSWSH origin check.
- `janissary ws <url>` CLI subcommand.
- `tests/unit/test_websocket.py` — 13 tests, real in-process servers.

## P2.1 — GraphQL fuzzer (DONE)

- `src/janissary/integrations/graphql.py` — client, builders,
  `detect`, `enumerate_fields`, `depth_probe`, `alias_probe`,
  `fuzz_arguments`.
- `janissary graphql <url>` CLI subcommand.
- `tests/unit/test_graphql.py` — 25 tests.

## P1.4 — Platform fingerprint (DONE)

- `src/janissary/recon/fingerprint.py` — `Fingerprinter`,
  `fingerprint()`.
- `janissary fingerprint <url>` CLI subcommand.
- `tests/unit/test_fingerprint.py` — 15 tests.

## P1.3 — XML-RPC multicall harness (DONE)

- `src/janissary/integrations/xmlrpc.py` — encoder, decoder,
  `XmlRpcClient`, `detect`, `bruteforce_multicall`, `pingback_probe`.
- `tests/unit/test_xmlrpc.py` — 26 tests.

## P1.2 — WAF detector + adaptive pacer (DONE)

- `src/janissary/recon/waf.py` — `WAFDetector`, 10 vendor signatures.
- `src/janissary/recon/pacer.py` — `AdaptivePacer`, `PacerConfig`.
- Wired into `engine/scanner.py`; `--no-waf` flag.
- `tests/unit/test_waf.py` (10), `tests/unit/test_pacer.py` (9),
  `tests/integration/test_scanner_recon.py` (4).

---

## P3.2 - Nuclei runner (DONE)

- src/janissary/attack/nuclei.py provides NucleiRunner, which shells
  out to the nuclei binary, requests JSONL output, and parses each
  line into a NucleiFinding.
- parse_nuclei_line() handles blank lines, non-JSON, non-dict JSON,
  and objects without a template-id by returning None. It accepts
  both 'template-id' and 'templateID' spellings, and both list and
  comma-separated-string forms for tags and reference.
- Guard rails, three layers:
    1. attack_confirm=True required at construction.
    2. nuclei binary must resolve on PATH (NucleiNotFound otherwise).
    3. templates must be a non-empty list. The runner refuses to use
       nuclei's default template set.
- Exit-code handling: 0 clean, 1 findings (not an error), anything
  else marks the run aborted.
- Timeout is clamped to 1800s. Rate limit defaults to 50.
- CLI: janissary attack nuclei <url> --templates a,b --severity X
  --tags Y --attack-confirm.
- tests/unit/test_nuclei.py - 22 tests, subprocess.run mocked.

Suite: 257 tests passing. Ruff clean.

---

## Current step

P3.3 - Agent / FindingStore / PlatformKB.

Not yet started. Design notes:

- This is the last Phase 3 module. It is the piece that turns
  JANISSARY from a set of scanners into a platform: a place for
  findings to live, a place for platform knowledge to live, and an
  agent that ties the two together.
- Likely home: src/janissary/agent/ as a new package. Submodules:
    - finding_store.py - append-only store of findings, keyed by
      target + hash. JSON or SQLite. No server.
    - platform_kb.py - the knowledge base. Static data describing
      known platforms (from recon/fingerprint and recon/admin) and
      the attack surfaces each one exposes. Eventually this drives
      which modules to run against which target.
    - agent.py - the orchestrator. Takes a target, fingerprints it,
      queries the KB, picks modules, runs them, writes findings to
      the store.
- Open question: does the agent need a config file, or is it
  purely CLI-driven? Lean toward CLI-driven for now; config can
  come when there is a real need.
- The store must be readable by the reporting layer. Keep it
  format-agnostic in shape: a list of dicts with stable keys.
- Tests: tests/unit/test_finding_store.py, tests/unit/test_platform_kb.py,
  tests/unit/test_agent.py. Mocked sessions, no live network.
- The agent is the natural place to wire in the AdaptivePacer and
  WAFDetector from recon, so a full agent run stays stealthy.
## Git status note

All work through P3.1 is committed and pushed. The legal framework,
the ASCENSION roadmap, the countdown tracker, and P3.1 are on GitHub
at the latest `main`.

---

## Vision

See `JANISSARY_ASCENSION.md` for the full roadmap to top-20 DAST
ranking, the competitive positioning, and the 12-month timeline.

Track progress:

    python tools/ascension.py
