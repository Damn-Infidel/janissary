"""Command-line entry point for JANISSARY.

Exit codes follow the sysexits.h convention:
    0   scan completed, no findings
    1   scan completed, findings present
    2   scan aborted (network error, preflight failure)
    64  usage error (missing or invalid arguments)
"""

from __future__ import annotations

import argparse
import json
import sys

from janissary import __version__
from janissary.engine.scanner import Scanner, ScanSummary

# -------------------------------------------------------------------
# OUTPUT HELPERS
# -------------------------------------------------------------------

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

def _summary_to_dict(summary: ScanSummary) -> dict:
    return {
        "target": summary.target,
        "params": summary.params,
        "method": summary.method,
        "total_requests": summary.total_requests,
        "finding_count": summary.finding_count,
        "aborted": summary.aborted,
        "abort_reason": summary.abort_reason,
        "baselines": summary.baselines,
        "waf": summary.waf,
        "pacer": summary.pacer,
        "findings": [
            {
                "param": f.param,
                "payload_name": f.payload_name,
                "payload_value": f.payload_value,
                "category": f.category,
                "severity": f.severity,
                "finding_type": f.finding_type,
                "detail": f.detail,
                "response_status": f.response_status,
                "response_length": f.response_length,
                "response_time": f.response_time,
                "reflection_context": f.reflection_context,
                "response_content_type": f.response_content_type,
            }
            for f in summary.findings
        ],
    }

def _print_banner() -> None:
    print("JANISSARY — differential DAST")
    print("=" * 60)

def _print_summary(summary: ScanSummary) -> None:
    print()
    print("=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"  Target:          {summary.target}")
    print(f"  Parameters:      {', '.join(summary.params)}")
    print(f"  Method:          {summary.method}")
    print(f"  Total requests:  {summary.total_requests}")
    print(f"  Findings:        {summary.finding_count}")

    if summary.aborted:
        print(f"  ABORTED:         {summary.abort_reason}")
        return

    if summary.waf is not None:
        print()
        print("  WAF:")
        if summary.waf.get("detected"):
            print(
                f"    detected=True vendor={summary.waf.get('vendor')} "
                f"confidence={summary.waf.get('confidence')}"
            )
        else:
            print("    detected=False")

    if summary.pacer is not None:
        print()
        print("  Pacer:")
        print(
            f"    final_delay={summary.pacer.get('current_delay')}s "
            f"events={summary.pacer.get('events')}"
        )

    if summary.baselines:
        print()
        print("  Baselines:")
        for param, b in summary.baselines.items():
            print(
                f"    {param}: samples={b['samples']} "
                f"mean={b['mean_elapsed']}s std={b['std_elapsed']}s "
                f"stable_body={b['stable_body']}"
            )

    if summary.findings:
        print()
        print("  Findings by severity:")
        by_sev: dict[str, int] = {}
        for f in summary.findings:
            by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        for sev in sorted(by_sev, key=lambda s: SEV_ORDER.get(s, 99)):
            print(f"    {sev.upper():10} {by_sev[sev]}")

# -------------------------------------------------------------------
# SUBCOMMANDS
# -------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> int:
    if getattr(args, "show_version", False):
        print(f"janissary {__version__}")
        return 0

    if not args.url:
        print("[!] scan requires --url", file=sys.stderr)
        return 64
    if not args.params:
        print("[!] scan requires --params", file=sys.stderr)
        return 64

    params = [p.strip() for p in args.params.split(",") if p.strip()]
    if not params:
        print("[!] --params produced no valid parameter names", file=sys.stderr)
        return 64

    proxies = None
    if args.proxy:
        proxies = {"http": args.proxy, "https": args.proxy}

    scanner = Scanner(
        target=args.url,
        params=params,
        method=args.method,
        timeout=args.timeout,
        baseline_count=args.baseline_count,
        delay=args.delay,
        stealth=args.stealth,
        proxies=proxies,
        detect_waf=not args.no_waf,
    )

    if not args.quiet:
        _print_banner()
        print(f"[*] Scanning {args.url}")
        print(f"[*] Parameters: {', '.join(params)}")
        print(f"[*] Method: {args.method}")
        print(f"[*] Baseline samples: {args.baseline_count}")
        print()

    summary = scanner.scan(quiet=args.quiet)

    if not args.quiet:
        _print_summary(summary)

    if args.export:
        payload = _summary_to_dict(summary)
        ext = args.export.lower().rsplit(".", 1)[-1]
        if ext == "json":
            with open(args.export, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
        elif ext == "sarif":
            _write_sarif(summary, args.export)
        else:
            with open(args.export, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
        print(f"[*] Results exported to {args.export}")

    if summary.aborted:
        return 2
    if summary.findings:
        return 1
    return 0

def cmd_creds(args: argparse.Namespace) -> int:
    from janissary.credentials.export import export_credentials
    from janissary.credentials.git_history import scan_git_history
    from janissary.credentials.scanner import scan_directory

    if getattr(args, "scan_git", False):
        if not args.path:
            print("[!] --scan-git requires a repository path",
                  file=sys.stderr)
            return 64
        try:
            findings = scan_git_history(
                args.path,
                max_commits=getattr(args, "max_commits", None),
                enable_entropy=not getattr(args, "no_entropy", False),
                quiet=getattr(args, "quiet", False),
            )
        except ValueError as exc:
            print(f"[!] {exc}", file=sys.stderr)
            return 66
        print(f"[*] {len(findings)} finding(s)")
        if args.export:
            export_credentials(findings, args.export)
        return 0 if not findings else 1

    try:
        findings = scan_directory(
            args.path,
            env_only=getattr(args, "env_only", False),
            verbose=not getattr(args, "quiet", False),
            enable_entropy=not getattr(args, "no_entropy", False),
        )
    except NotADirectoryError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 66

    print(f"[*] {len(findings)} finding(s)")

    if args.export:
        export_credentials(findings, args.export)
    return 0 if not findings else 1

def cmd_fingerprint(args: argparse.Namespace) -> int:
    from janissary.recon.fingerprint import fingerprint as run_fingerprint

    proxies = None
    if getattr(args, "proxy", None):
        proxies = {"http": args.proxy, "https": args.proxy}

    fp = run_fingerprint(
        args.url,
        timeout=args.timeout,
        proxies=proxies,
        probe_cms_paths=not getattr(args, "no_cms_paths", False),
        probe_favicon=not getattr(args, "no_favicon", False),
    )

    if not args.quiet:
        print("JANISSARY — platform fingerprint")
        print("=" * 60)
        print(f"  Target:         {fp.target}")
        print(f"  Reachable:      {fp.reachable} (HTTP {fp.status})")
        print(f"  Server:         {fp.server or '-'}")
        print(f"  X-Powered-By:   {fp.powered_by or '-'}")
        print(f"  CMS:            {fp.cms or '-'} "
              f"(confidence {fp.cms_confidence:.2f})")
        print(f"  Technologies:   {', '.join(fp.technologies) or '-'}")
        print(f"  Meta generator: {fp.meta_generator or '-'}")
        print(f"  Favicon hash:   {fp.favicon_hash or '-'}")
        print(f"  Title:          {fp.title or '-'}")
        if fp.cookies:
            print(f"  Cookies:        {', '.join(fp.cookies)}")
        if fp.paths_found:
            print("  Paths:")
            for path, status in sorted(fp.paths_found.items()):
                print(f"    {status}  {path}")
        if fp.notes:
            print("  Notes:")
            for n in fp.notes:
                print(f"    - {n}")

    if args.export:
        with open(args.export, "w", encoding="utf-8") as fh:
            json.dump(fp.to_dict(), fh, indent=2)
        print(f"[*] Results exported to {args.export}")

    return 0 if fp.reachable else 2

def cmd_graphql(args: argparse.Namespace) -> int:
    from janissary.integrations.graphql import (
        GraphQLClient,
        alias_probe,
        depth_probe,
        detect,
        enumerate_fields,
        fuzz_arguments,
    )

    proxies = None
    if getattr(args, "proxy", None):
        proxies = {"http": args.proxy, "https": args.proxy}

    if not args.quiet:
        print("JANISSARY — GraphQL recon")
        print("=" * 60)
        print(f"[*] Target: {args.url}")
        if args.endpoint_path:
            print(f"[*] Endpoint path: {args.endpoint_path}")
        print()

    profile = detect(
        args.url,
        timeout=args.timeout,
        proxies=proxies,
        explicit_path=args.endpoint_path,
    )

    if not profile.reachable:
        if not args.quiet:
            print("[!] No reachable GraphQL endpoint found")
            for n in profile.notes:
                print(f"    - {n}")
        return 2

    if not args.quiet:
        print(f"[*] Endpoint: {profile.endpoint}")
        print(f"    introspection_enabled={profile.introspection_enabled}")
        print(f"    query_type={profile.query_type or '-'}")
        print(f"    mutation_type={profile.mutation_type or '-'}")
        print(f"    type_count={profile.type_count}")
        print(f"    batched_queries={profile.batched_queries}")
        print(f"    suggestions_supported={profile.suggestions_supported}")

    client = GraphQLClient(profile.endpoint, timeout=args.timeout, proxies=proxies)
    extras: dict = {}

    if getattr(args, "enumerate_fields", False):
        names = enumerate_fields(client)
        extras["fields"] = names
        if not args.quiet:
            print(f"[*] Fields discovered via suggestions: {len(names)}")
            for n in names[:30]:
                print(f"    {n}")

    if getattr(args, "depth_probe", False):
        depth, msg = depth_probe(client)
        extras["max_depth"] = depth
        extras["depth_refusal"] = msg
        if not args.quiet:
            print(f"[*] Depth: max accepted={depth} refusal={msg[:60]!r}")

    if getattr(args, "alias_probe", False):
        count, msg = alias_probe(client)
        extras["max_aliases"] = count
        extras["alias_refusal"] = msg
        if not args.quiet:
            print(f"[*] Aliases: max accepted={count} refusal={msg[:60]!r}")

    if getattr(args, "fuzz_args", None):
        # --fuzz-args FIELD:ARG
        field, _, arg = args.fuzz_args.partition(":")
        if not field or not arg:
            print("[!] --fuzz-args requires FIELD:ARG", file=sys.stderr)
            return 64
        results = fuzz_arguments(client, field, arg)
        extras["fuzz"] = [r.to_dict() for r in results]
        if not args.quiet:
            print(f"[*] Fuzzed {field}({arg}) with {len(results)} payloads")
            for r in results:
                errs = "; ".join(r.errors)[:60]
                print(f"    {r.payload_name:15} status={r.status} {errs}")

    if args.export:
        doc = profile.to_dict()
        doc.update(extras)
        with open(args.export, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
        print(f"[*] Results exported to {args.export}")

    return 0


def cmd_websocket(args: argparse.Namespace) -> int:
    from janissary.integrations.websocket import scan_sync

    if not args.quiet:
        print("JANISSARY — WebSocket recon")
        print("=" * 60)
        print(f"[*] Target: {args.url}")
        print()

    try:
        profile = scan_sync(
            args.url,
            timeout=args.timeout,
            origin=args.origin,
            evil_origin=args.evil_origin,
            echo_payload=args.payload,
        )
    except Exception as exc:
        print(f"[!] WebSocket scan failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(f"  Reachable:      {profile.reachable}")
        print(f"  Scheme:         {profile.scheme or '-'}")
        print(f"  Subprotocol:    {profile.subprotocol or '-'}")
        print(f"  Server:         {profile.server_header or '-'}")
        print(f"  Msgs sent/rcvd: {profile.messages_sent}/{profile.messages_received}")
        if profile.findings:
            print()
            print("  Findings:")
            for f in profile.findings:
                print(f"    {f.severity.upper():8} [{f.category}] {f.detail}")
        if profile.notes:
            print()
            print("  Notes:")
            for n in profile.notes:
                print(f"    - {n}")

    if args.export:
        with open(args.export, "w", encoding="utf-8") as fh:
            json.dump(profile.to_dict(), fh, indent=2)
        print(f"[*] Results exported to {args.export}")

    if not profile.reachable:
        return 2
    return 1 if profile.findings else 0


def _write_sarif(summary: ScanSummary, path: str) -> None:
    """Emit a minimal SARIF 2.1.0 document."""
    results = []
    for f in summary.findings:
        results.append(
            {
                "ruleId": f"{f.category}:{f.finding_type}",
                "level": "error" if f.severity in ("critical", "high") else "warning",
                "message": {"text": f.detail},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": summary.target},
                        }
                    }
                ],
                "properties": {
                    "param": f.param,
                    "payload": f.payload_name,
                },
            }
        )

    doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "JANISSARY",
                        "version": __version__,
                        "informationUri": "https://github.com/yourorg/janissary",
                    }
                },
                "results": results,
            }
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)

# -------------------------------------------------------------------
# PARSER
# -------------------------------------------------------------------

class _ArgumentParser(argparse.ArgumentParser):
    """Argparse subclass that exits with 64 (EX_USAGE) on errors."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(64, f"{self.prog}: error: {message}\n")

def build_parser() -> argparse.ArgumentParser:
    p = _ArgumentParser(
        prog="janissary",
        description="JANISSARY — differential DAST scanner",
    )
    p.add_argument("--version", action="version", version=f"janissary {__version__}")

    sub = p.add_subparsers(dest="command")

    # -- scan -----------------------------------------------------
    scan = sub.add_parser("scan", help="scan an HTTP endpoint")
    scan.add_argument("-u", "--url", default=None, help="target URL")
    scan.add_argument(
        "-p", "--params", default=None, help="comma-separated parameter names"
    )
    scan.add_argument("--method", choices=["GET", "POST"], default="GET")
    scan.add_argument("--timeout", type=float, default=10.0)
    scan.add_argument("--delay", type=float, default=0.0)
    scan.add_argument("--baseline-count", type=int, default=10)
    scan.add_argument("--stealth", action="store_true")
    scan.add_argument(
        "--no-waf", action="store_true",
        help="skip WAF detection probe phase",
    )
    scan.add_argument(
        "--proxy", default=None, help="HTTP proxy URL (e.g. http://127.0.0.1:8080)"
    )
    scan.add_argument(
        "--export", default=None, help="write results to a .json or .sarif file"
    )
    scan.add_argument("--quiet", action="store_true")
    scan.add_argument(
        "--version",
        dest="show_version",
        action="store_true",
        help="print version and exit",
    )
    scan.set_defaults(func=cmd_scan)

    # -- creds ----------------------------------------------------
    creds = sub.add_parser("creds", help="scan for leaked credentials")
    creds.add_argument("path", help="directory to scan (or repo with --scan-git)")
    creds.add_argument("--scan-git", action="store_true",
                       help="scan git history instead of the working tree")
    creds.add_argument("--max-commits", type=int, default=None,
                       help="cap the number of commits scanned")
    creds.add_argument("--env-only", action="store_true",
                       help="scan only .env and config files")
    creds.add_argument("--no-entropy", action="store_true",
                       help="disable Shannon entropy fallback")
    creds.add_argument("--export", default=None,
                       help="write findings to a .json or .csv file")
    creds.add_argument("--quiet", action="store_true")
    creds.set_defaults(func=cmd_creds)

    # -- fingerprint ---------------------------------------------
    fp = sub.add_parser("fingerprint", help="fingerprint a target")
    fp.add_argument("url", help="target URL")
    fp.add_argument("--timeout", type=float, default=10.0)
    fp.add_argument("--proxy", default=None,
                    help="HTTP proxy URL (e.g. http://127.0.0.1:8080)")
    fp.add_argument("--no-cms-paths", action="store_true",
                    help="skip CMS path probes")
    fp.add_argument("--no-favicon", action="store_true",
                    help="skip favicon hash")
    fp.add_argument("--export", default=None,
                    help="write the fingerprint to a .json file")
    fp.add_argument("--quiet", action="store_true")
    fp.set_defaults(func=cmd_fingerprint)

    # -- graphql --------------------------------------------------
    gql = sub.add_parser("graphql", help="recon a GraphQL endpoint")
    gql.add_argument("url", help="target base URL or endpoint")
    gql.add_argument("--endpoint-path", default=None,
                     help="explicit endpoint path (e.g. /graphql)")
    gql.add_argument("--timeout", type=float, default=10.0)
    gql.add_argument("--proxy", default=None,
                     help="HTTP proxy URL (e.g. http://127.0.0.1:8080)")
    gql.add_argument("--enumerate-fields", action="store_true",
                     help="try to enumerate fields via error suggestions")
    gql.add_argument("--depth-probe", action="store_true",
                     help="find the maximum accepted query depth")
    gql.add_argument("--alias-probe", action="store_true",
                     help="find the maximum accepted alias count")
    gql.add_argument("--fuzz-args", default=None, metavar="FIELD:ARG",
                     help="fuzz FIELD(ARG: <payload>) with the built-in set")
    gql.add_argument("--export", default=None,
                     help="write the profile to a .json file")
    gql.add_argument("--quiet", action="store_true")
    gql.set_defaults(func=cmd_graphql)

    # -- ws -------------------------------------------------------
    ws = sub.add_parser("ws", help="recon a WebSocket endpoint")
    ws.add_argument("url", help="WebSocket URL (ws:// or wss://)")
    ws.add_argument("--timeout", type=float, default=10.0)
    ws.add_argument("--origin", default=None,
                    help="Origin header to send on the baseline connect")
    ws.add_argument("--evil-origin", default="http://evil.example.com",
                    help="Origin to try for cross-site WebSocket hijacking")
    ws.add_argument("--payload", default="<script>alert(1)</script>",
                    help="payload for the echo probe")
    ws.add_argument("--export", default=None,
                    help="write the profile to a .json file")
    ws.add_argument("--quiet", action="store_true")
    ws.set_defaults(func=cmd_websocket)

    return p

# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
