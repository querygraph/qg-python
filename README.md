# QueryGraph Python

Python port of the QueryGraph AI Navigator semantic layer.

It mirrors the Rust implementation in `../qg-rust`:

- Croissant JSON-LD dataset metadata
- CDIF discovery/access/profile projection
- deterministic `did:oyd` identity documents
- ODRL permissions and prohibitions
- an AI Navigator bundle builder
- a CLI compatible with the Rust commands

## Run

```bash
python -m querygraph navigator \
  --dataset-name "Hazard vocabulary" \
  --description "Controlled vocabulary with multilingual technical terms" \
  --landing-page "https://querygraph.ai/datasets/hazards" \
  --data-url "https://querygraph.ai/datasets/hazards.csv"
```

## Test

```bash
python -m pytest
```

The test suite includes equivalence checks against the sibling Rust implementation.
