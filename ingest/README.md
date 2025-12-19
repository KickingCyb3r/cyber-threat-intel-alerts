Ingest
Overview

The ingest directory contains all external data collection logic for the Cyber Threat Intelligence (CTI) ingestion project.

This layer is responsible for retrieving, validating, and logging raw threat intelligence data from authoritative sources. It intentionally does not perform analysis, enrichment, alerting, or long-term storage.

Responsibilities

The ingest layer is designed to:

Fetch live CTI data from external sources

Handle network communication (timeouts, retries)

Perform basic structural validation

Generate repeatable output artifacts

Log execution status for operational visibility

Each data source is implemented as a separate script to maintain modularity and scalability.

Current Data Sources
CISA Known Exploited Vulnerabilities (KEV)

Script: cisa_kev.py

Source: CISA KEV JSON feed

Purpose: Ingest high-confidence vulnerabilities actively exploited in the wild

Outputs:

output/kev_latest.json

Timestamped snapshots (output/kev_YYYYMMDD_HHMMSSZ.json)

Logs:

logs/kev_ingest.log

Additional sources (e.g., AlienVault OTX, Dark Reading) will be added incrementally once ingestion reliability is fully validated.
