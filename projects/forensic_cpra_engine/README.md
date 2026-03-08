# Forensic CPRA Engine (MVP)

MVP commands:

- `python -m app.cli vault ingest --case-dir data/CASE_BUNDLES/case_YYYYMMDD_slug`
- `python -m app.cli cpra analyze --case data/CASE_BUNDLES/case_YYYYMMDD_slug/case.yaml`

Outputs are written under each case bundle:
- `00_VAULT/`
- `02_OUTPUT/run_YYYYMMDD_HHMMSS/`
