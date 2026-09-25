# JANISSARY — Port Workflow Tracker

## STATUS: PHASE 3 — IN PROGRESS
## NEXT: P3.2 — Nuclei runner
## LAST COMPLETED: P3.1 — SQLi UNION extractor (235 tests pass)

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
- [ ] P3.2 Nuclei runner (expose NucleiRunner, drop stub)
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

## Current step

P3.2 - Nuclei runner.

STATUS: PAUSED at a design decision. Nothing coded yet.

### OPEN DECISION: where does the Nuclei module live?

**Option A - src/janissary/attack/nuclei.py**

- Nuclei is active exploitation. Everything in attack/ carries the
  --attack-confirm gate.
- Consistent with P3.1: extraction and exploitation live together.
- The gate is the legal mechanism. Placing the module here means it
  inherits that framing without argument.

**Option B - src/janissary/integrations/nuclei.py**

- Nuclei is an external binary. integrations/ already holds the
  protocol clients (xmlrpc, graphql, websocket).
- The module's job is mostly subprocess + JSONL parsing.
- BUT: integrations/ modules do not all carry the attack-confirm
  gate, so the gate would have to be added explicitly.

**Leaning:** Option A, because the gate is what matters legally and
attack/ already establishes it. Confirm before coding.

### Design notes (once placement is decided)

- Shell out via subprocess; stream JSONL; parse each line.
- Do not reimplement Nuclei's template engine.
- Require --attack-confirm; refuse if nuclei is not on PATH;
  require an explicit --templates list rather than the default set.
- CLI: janissary attack nuclei <url> with --templates, --severity,
  --attack-confirm, --timeout, --export, --quiet.
- Tests: tests/unit/test_nuclei.py, mocking subprocess.run.
- Confirm DSGL position with Defence Export Controls before any
  public release.

---
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
