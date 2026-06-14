from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from querygraph.typedid import TypeDidEnvelope, sha256_hex


class OpenLineageRunEvent(BaseModel):
    eventType: str = "COMPLETE"
    eventTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run: dict[str, Any]
    job: dict[str, Any]
    inputs: list[dict[str, Any]] = Field(default_factory=list)
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    producer: str = "https://querygraph.ai/qg-python"
    schemaURL: str = "https://openlineage.io/spec/2-0-2/OpenLineage.json"

    @classmethod
    def for_agent_run(
        cls,
        *,
        request: TypeDidEnvelope,
        job_name: str,
        inputs: list[str],
        outputs: list[str],
        namespace: str = "querygraph.python",
    ) -> "OpenLineageRunEvent":
        return cls(
            run={
                "runId": f"querygraph-python-{request.signature[-12:]}",
                "facets": {
                    "queryGraph_typeDid": {
                        "_producer": "https://querygraph.ai/qg-python",
                        "_schemaURL": "https://querygraph.ai/schemas/openlineage/querygraph-typedid-facet/0.1.0.json",
                        "protocol": request.protocol,
                        "conversationId": request.conversation_id,
                        "payloadSha256": request.payload_sha256,
                        "signature": request.signature,
                    }
                },
            },
            job={"namespace": namespace, "name": job_name},
            inputs=[{"namespace": "sail", "name": item} for item in inputs],
            outputs=[{"namespace": "querygraph", "name": item} for item in outputs],
        )

    def event_hash(self) -> str:
        return sha256_hex(self.model_dump_json(exclude_none=True))


class LineageAttestation(BaseModel):
    issuer: str
    subject: str
    event_hash: str
    merkle_root: str
    signature_type: str = "QueryGraphDemoSha256Signature"
    verification_method: str
    signature: str
    signed_payload_sha256: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_event(
        cls,
        *,
        issuer: str,
        subject: str,
        event_hash: str,
    ) -> "LineageAttestation":
        created_at = datetime.now(UTC)
        merkle_root = sha256_hex(f"querygraph-lineage\n{event_hash}")
        payload = "\n".join(
            [
                "querygraph-lineage-attestation-v1",
                f"issuer:{issuer}",
                f"subject:{subject}",
                f"event_hash:{event_hash}",
                f"merkle_root:{merkle_root}",
                f"created_at:{created_at.isoformat()}",
            ]
        )
        return cls(
            issuer=issuer,
            subject=subject,
            event_hash=event_hash,
            merkle_root=merkle_root,
            verification_method=f"{issuer}#querygraph-demo-key",
            signature=f"sha256:{sha256_hex(payload)}",
            signed_payload_sha256=sha256_hex(payload),
            created_at=created_at,
        )


def append_jsonl(path: str | Path, value: BaseModel | dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, sort_keys=True))
        handle.write("\n")
    return target
