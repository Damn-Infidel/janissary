# JANISSARY

**Differential DAST for teams who need results they can trust.**

> ### Authorised use only
>
> JANISSARY is a dual-use security testing tool. Use it **only**
> against systems you own, or systems you have prior written
> permission to test.
>
> By running any network command you accept the
> [Terms of Use](LEGAL.md). Review with `janissary terms show`.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)

---

## Why JANISSARY

Most DAST tools are either expensive enterprise platforms or raw scripts that produce unusable noise. JANISSARY is different in three specific ways:

**Differential detection eliminates false positives by design.** Every finding is gated by a baseline comparison. No finding is ever emitted from a single response alone.

**WAF-aware pacing keeps you under the radar.** JANISSARY detects Cloudflare, Akamai, Sucuri, Imperva, AWS WAF, F5, Barracuda, ModSecurity, Wordfence, and Fastly, then backs off on blocks and recovers on clean streaks.

**Multi-protocol coverage.** HTTP, XML-RPC, GraphQL, and WebSocket, combined into a single agent run.

---

## Install

```bash
pip install janissary
```

---

## Quickstart

Accept the Terms of Use (required once before any network command):

```bash
janissary terms accept
```

Scan a single endpoint:

```bash
janissary scan -u "https://target.example/search?q=test" -p q
```

Scan a Git repository for leaked credentials:

```bash
janissary creds ./my-repo --scan-git
```

Fingerprint a target:

```bash
janissary fingerprint https://target.example
```

Probe for admin panels:

```bash
janissary admin https://target.example
```

---

## Commands

| Command | What it does |
|---|---|
| `scan` | HTTP scanning: SQLi, XSS, SSRF, traversal, cmdi |
| `creds` | Credential discovery in tree or Git history |
| `fingerprint` | CMS and technology identification |
| `graphql` | GraphQL detection and field enumeration |
| `ws` | WebSocket recon |
| `admin` | Admin panel discovery, 18 platforms |
| `agent` | Orchestrates recon, persists findings |
| `terms` | Show, check, or accept Terms of Use |
| `attack sqli-union` | UNION extractor (gated) |
| `attack nuclei` | Nuclei runner (gated) |

Run `janissary --help` for full flags.

---

## Attack modules

The `attack` subcommands are opt-in. They require `--attack-confirm` in addition to the Terms-of-Use gate. Neither alone is enough.

- **`attack sqli-union`** - extracts DBMS version, current database, database list, and table list from a vulnerable parameter. Hard limits: 32 columns, 100 rows, 64KB. Aborts on instability.
- **`attack nuclei`** - shells out to the Nuclei binary, streams JSONL, parses findings. Requires an explicit template list; refuses to run Nuclei's default set.

---

## Agent

The `agent` command ties the recon modules together: fingerprint, detect WAF, consult the platform knowledge base, run applicable modules, persist findings.

```bash
janissary agent https://target.example --attack-confirm --store findings.json
```

---

## Status

**Phase 3 complete.** 303 tests passing. All subsystems shipped:

- Phase 0 - green baseline
- Phase 1 - credentials, Git history, WAF + pacer, XML-RPC, fingerprint
- Phase 2 - GraphQL, WebSocket, admin probe
- Phase 3 - SQLi UNION extractor, Nuclei runner, agent

Roadmap: [JANISSARY_ASCENSION.md](JANISSARY_ASCENSION.md).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

Apache 2.0 for the source code. See [LICENSE](LICENSE).

Use is additionally governed by the [Terms of Use](LEGAL.md), which supplement and do not replace the Apache 2.0 licence.
