# QueryGraph Python

Python ecosystem for the QueryGraph AI Navigator.

It mirrors and extends the Rust implementation in `../qg-rust`:

- Croissant JSON-LD dataset metadata
- CDIF discovery/access/profile projection
- deterministic `did:oyd` identity documents
- ODRL permissions and prohibitions
- OSI semantic models over Croissant fields and Sail columns
- TypeDID agents modeled with Pydantic
- optional LangChain adapters for governed agent tools
- OpenLineage events and DID-style attestations
- PySpark helpers for querying a local Sail warehouse
- a CLI compatible with the Rust semantic bundle commands

The design goal is Python-native ergonomics over the same governed lakehouse:
Rust loads and verifies the warehouse; Python gives notebooks, PySpark users,
LangChain agents, and data scientists a typed interop layer.

## Stack versions

This port tracks the same coordinated QueryGraph stack releases as `../qg-rust`:

- **Grust 0.11.0 "Crab"** — the property-graph + GQL/Cypher substrate.
- **TypeSec 0.10.0 "Murano"** — the typed security fabric; the Pydantic
  `TypeDidEnvelope` mirrors Murano's audit-safe attestation (action, resource,
  privacy level, negotiated profile, and an envelope digest).
- **LakeCat 0.2.0 "Lynx"** — the thin Iceberg REST catalog boundary.

See `../qg-rust/docs/blog/announcing-querygraph-stack.md` for the full story.

## Install

Core metadata and TypeDID/Pydantic support:

```bash
uv sync
```

Optional PySpark/Sail support:

```bash
uv sync --extra lakehouse
```

Optional LangChain tool adapters:

```bash
uv sync --extra agents
```

Everything:

```bash
uv sync --extra all
```

## Build a Semantic Bundle

```bash
python -m querygraph navigator \
  --dataset-name "Hazard vocabulary" \
  --description "Controlled vocabulary with multilingual technical terms" \
  --landing-page "https://querygraph.ai/datasets/hazards" \
  --data-url "https://querygraph.ai/datasets/hazards.csv"
```

## QG Lakehouse Agent Story

```bash
python -m querygraph qglake-story --pretty
```

This produces a Pydantic TypeDID multi-agent run: supervisor, finance, energy,
mobility, climate-health, reference, restricted-data broker, synthesis,
OpenLineage, and DID attestation.

## Query Sail with PySpark

Start Sail from the Rust project after the lakehouse has been loaded:

```bash
cd ../qg-rust
sail spark server --port 50051
```

In another shell:

```bash
cd ../qg-python
uv sync --extra lakehouse
uv run querygraph lakehouse-register \
  --manifest ../qg-rust/.querygraph/lakehouse/manifest/load-report.json \
  --warehouse ../qg-rust/spark-warehouse
uv run querygraph audit-register --warehouse ../qg-rust/spark-warehouse
uv run querygraph pyspark-examples
```

Open a shell:

```bash
uv run pyspark --remote sc://127.0.0.1:50051
```

Then query the registered views:

```python
spark.sql("SELECT COUNT(*) FROM global_temp.government_finance__countydata").show()
spark.sql("SELECT quantity, value, unit FROM global_temp.codata_constants_2022__codata_constants_2022 LIMIT 5").show(truncate=False)
spark.sql("SELECT event_hash, event_type, job_name FROM global_temp.openlineage_events LIMIT 10").show(truncate=False)
```

## OSI with Semantic Croissant

```bash
uv run python examples/osi_semantic_croissant.py
```

The example starts with concrete Semantic Croissant fields and projects them
into an OSI semantic model with ontology terms and Sail SQL expressions.

## TypeDID Agents with LangChain

```bash
uv sync --extra agents
uv run python examples/typedid_langchain_agents.py
```

The agents are Pydantic models first. When LangChain is installed, a
`TypeDidLangChainToolAdapter` exposes the same governed agent as a LangChain
`StructuredTool`.

## Test

```bash
uv run python -m pytest
```

The test suite includes equivalence checks against the sibling Rust implementation.
