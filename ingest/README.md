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


