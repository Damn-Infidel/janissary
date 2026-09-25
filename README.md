# JANISSARY

**Automated offensive security platform for small teams.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)

JANISSARY scans web endpoints for SQL injection, XSS, SSRF, and
path traversal, discovers leaked credentials in Git history and
config files, and produces SARIF reports that plug into GitHub
Advanced Security.

Built for penetration testers and small security teams who need
Burp-class automation without Burp-class pricing.

## Why JANISSARY

Most DAST tools fall into two camps: expensive enterprise platforms
(Invicti, Acunetix) or raw scripts that produce unusable noise.
JANISSARY sits in between: automated, CI-friendly, and tuned for low
false positives.

- **Differential detection engine** -- every finding is gated by a
  baseline comparison, not a keyword match.
- **Credential discovery** -- scans Git history, env files, and config
  files for leaked secrets.
- **WAF-aware pacing** -- detects Cloudflare, Akamai, Sucuri, and
  Imperva, then automatically adjusts delay, concurrency, and
  User-Agent to avoid triggering blocks.
- **Nuclei integration** -- runs your existing Nuclei templates
  through the same baseline-gated pipeline.
- **SARIF and HTML output** -- plugs into GitHub Advanced Security,
  GitLab SAST, and DefectDojo.

## Install

```bash
pip install janissary
```

Or from source:

```bash
git clone https://github.com/yourorg/janissary
cd janissary
pip install -e ".[dev]"
```

## Quickstart

Scan a single endpoint:

```bash
janissary -u "https://target.example/api/search?q=test" -p q
```

Scan a POST form:

```bash
janissary -u "https://target.example/login" -p username,password --method POST
```

Scan a Git repository for leaked credentials:

```bash
janissary --scan-git ./my-repo
```

Export findings to SARIF:

```bash
janissary -u "https://target.example/api/search?q=test" -p q --sarif-export findings.sarif
```

## Detection Engine

JANISSARY's detection engine is built on differential analysis. For
each parameter, it collects a baseline of benign requests, normalizes
dynamic content (CSRF tokens, timestamps, session IDs), and then
compares each payload response against that baseline. A finding is
emitted only when multiple independent gates pass:

- The DB error pattern matches the payload response **and** does not
  match any baseline response.
- The XSS payload reflects unescaped **and** in an executable HTML
  context.
- The response time exceeds the declared sleep floor **and** the
  baseline has a trustworthy timing distribution.
- The status changes from 2xx to 5xx.

## Status

Early development. The differential detection engine is complete and
tested (28 tests, 91% coverage). The scanner that drives it is being
ported incrementally from the original v7.0.0 prototype.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We welcome payload
contributions, new detection gates, and integrations.

## Security

To report a vulnerability in JANISSARY itself, see
[SECURITY.md](SECURITY.md).

## License

Apache 2.0. See [LICENSE](LICENSE).
