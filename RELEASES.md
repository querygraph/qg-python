# QueryGraph Python releases

The Python port shares the version line and codenames of the Rust
implementation. The canonical release scheme and codename pool (birds of prey)
live in `../qg-rust/RELEASES.md`. Detailed per-release notes are in
[`CHANGELOG.md`](CHANGELOG.md).

## Release log

| Version | Codename | Notes |
|---|---|---|
| 0.3.0 | Goshawk | The **interoperability** release. Real Ed25519 signing (`crypto` extra) with `did:key` verification methods, verified cross-language by qg-rust. MCP server (`mcp-serve`), A2A Agent Card, OpenAI/Anthropic tool-schema export, async LangChain adapters, enriched OSI model, official OpenLineage 2-0-2 schema validation with spec-conformant UUIDv5 run ids, PyPI-ready packaging, CI. |
| 0.2.0 | Peregrine | Tracks Grust 0.11.0 "Crab", TypeSec 0.11.0 "Burano", LakeCat 0.2.1 "Lynx". TypeDID attestation parity (privacy / profile / envelope digest) with the Rust port. |
| 0.1.0 | — | (pre-codename) Initial Python port. |
