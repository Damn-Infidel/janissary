# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [7.1.0] - 2026-09-25

### Added
- Differential detection engine (replaces keyword matching)
- Baseline normalization for CSRF tokens, timestamps, UUIDs, session IDs
- DB-specific error patterns for MySQL, PostgreSQL, MSSQL, Oracle, SQLite
- 28 unit tests covering all false-positive gates
- 91% test coverage on the detection analyzer
- Apache 2.0 license
- Editable install via pyproject.toml with console entry point

### Changed
- DB error detection now requires database-specific patterns, not generic keywords
- Timing detection requires a variable baseline with std >= 0.05s
- Reflection detection requires executable context for XSS severity
- Status detection requires baseline to be 2xx and payload to be 5xx

### Removed
- Generic ERROR_KEYWORDS list (source of 80% of false positives)

## [7.0.0] - 2026-09-24

### Added
- Initial prototype release
