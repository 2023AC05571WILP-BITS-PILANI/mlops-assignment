# data_collection

This directory contains code and utilities responsible for collecting data from all sources used by the project.

Purpose:
- House ingestion scripts, connectors, and automations that fetch raw data from source systems (APIs, databases, files, streaming platforms, sensors, etc.).

Contents (expected):
- `ingest_*` scripts to pull data from various sources
- connector modules for APIs, databases, and cloud storage
- utilities for validation, deduplication, and schema enforcement
- configuration files (e.g. YAML) describing sources and credentials (credentials should be stored securely, not checked into VCS)

Guidelines:
- Keep source-specific logic modular and testable.
- Write idempotent ingestion jobs where possible.
- Log ingestion metadata (timestamps, source, row counts, errors) to `mounted_logs` or another centralized place.
- Prefer environment variables or a secrets manager for sensitive config.

Add new ingestion modules here following the conventions above.
