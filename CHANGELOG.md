# Changelog

All notable changes to the QueryGraph Python port are recorded here. The
codename pool and the shared version line live in [`RELEASES.md`](RELEASES.md);
the canonical scheme is in `../qg-rust/RELEASES.md`.

## 0.3.0-dev — unreleased

Interoperability release in progress, implementing the FABLE-REVIEW-1 P0 items
and quick wins (see `../FABLE-REVIEW-1.md`).

### Added
- **Real Ed25519 signing** (`querygraph.crypto`, extra: `crypto`). TypeDID
  envelopes and lineage attestations are now signed with real Ed25519 keys
  derived deterministically from agent seeds (mirroring Rust TypeSec
  `Ed25519DidKey::from_seed`), carry a W3C `did:key` `verification_method`,
  and verify with `TypeDidEnvelope.verify_signature()` /
  `LineageAttestation.verify()`. Without the extra, digests are explicitly
  prefixed `unsigned:sha256:` so they can never be mistaken for signatures.
- **MCP server** (`querygraph.mcp_server`, extra: `mcp`; CLI:
  `querygraph mcp-serve`). Exposes the governed semantic layer over the Model
  Context Protocol: `search_semantic_model`, `resolve_metric` (with dialect
  fallback), `check_access` (RBAC+ODRL dual gate; denials are receipts, not
  errors), `build_navigator_bundle`, `run_qglake_story`, `verify_envelope`,
  plus `qg://` resources.
- **Tool-schema export.** `TypeDidAgent.to_tool_schema(flavor="openai"|"anthropic")`
  emits standard JSON-Schema tool definitions accepted by OpenAI, Anthropic,
  Mistral, vLLM, Ollama, and most agent frameworks.
- **Async adapters.** `TypeDidLangChainToolAdapter.ainvoke()` and
  `as_async_tool()` for async agent runtimes.
- **Richer OSI model** ported from the semantic-layer research repos:
  structured `ai_context` (instructions/synonyms/examples), relationships,
  primary/unique keys, `SUPPORTED_DIALECTS`, `resolve_metric()` with
  ANSI_SQL/SAIL_SQL fallback, `find_by_synonym()`, and acceptance of upstream
  OSI documents that spell `semantic_model` as a list.
- **Cross-language qglake equivalence test** asserting governance semantics
  (specialist roster, denial pattern, evidence chain) match the Rust CLI.
- **Packaging**: `py.typed` marker, authors/urls/keywords/classifiers, new
  `crypto` and `mcp` extras, GitHub Actions CI (pytest matrix + build +
  twine check).

### Changed
- `TypeDidEnvelope` gains `verification_method`; unsigned envelopes are
  labelled `unsigned:sha256:` instead of `sha256:`. `LineageAttestation`
  signature types are now `QueryGraphEd25519Signature` /
  `QueryGraphUnsignedDigest` (was `QueryGraphDemoSha256Signature`).
- `langchain-core` dependency bounded `<2`.

## 0.2.0 "Peregrine" — 2026-06-26

First **named** release. Tracks the QueryGraph stack at Grust 0.11.0 "Crab",
TypeSec 0.11.0 "Burano", and LakeCat 0.2.1 "Lynx", and stays in lock-step with
the Rust implementation (`querygraph/qg-rust` v0.2.0).

### Added
- **TypeDID attestation parity.** `TypeDidEnvelope` gains `privacy`, `profile`,
  and `envelope_digest` fields, plus a `TYPEDID_PROFILE` constant, mirroring the
  Rust port's adoption of TypeSec 0.11 "Burano"'s audit-safe
  `VerifiedTypeDidMessage::attestation()`. `TypeDidEnvelope.create()` accepts
  `privacy` / `profile` (defaulting to `"secret"` and the
  `ed25519-x25519-chacha20` profile) and computes a deterministic
  `envelope_digest` that binds the attestation to the exact envelope without
  revealing the payload.
- **`RELEASES.md`** recording the shared version line and birds-of-prey codename
  pool; **`CHANGELOG.md`** (this file).
- **README "Stack versions"** section naming the three coordinated releases
  (Grust "Crab", TypeSec "Burano", LakeCat "Lynx") and pointing to the stack
  announcement.

### Changed
- Bumped the package version `0.1.0` → `0.2.0`.
- Updated stack references throughout to TypeSec 0.11.0 "Burano" and LakeCat
  0.2.1 "Lynx" (README, `typedid.py` docstrings).

### Compatibility
- The new `TypeDidEnvelope` fields are additive and default-valued, so existing
  callers and serialized payloads keep working.
- The Rust navigator-bundle equivalence test (`tests/test_rust_equivalence.py`)
  still passes: the `navigator` semantic bundle is byte-identical between the
  Python and Rust implementations. Full suite: 12 tests passing.

## 0.1.0 — initial Python port

Initial port of the QueryGraph AI Navigator semantic layer: Croissant/CDIF/DID/
ODRL projections, OSI semantic models, Pydantic TypeDID agents, optional
LangChain adapters, OpenLineage/DID attestations, PySpark/Sail helpers, and a
CLI compatible with the Rust semantic-bundle commands.
