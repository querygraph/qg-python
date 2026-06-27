from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, Field

from querygraph.did import DidDocument
from querygraph.odrl import Action, Policy


def sha256_hex(value: bytes | str) -> str:
    data = value.encode() if isinstance(value, str) else value
    return sha256(data).hexdigest()


class AccessReceipt(BaseModel):
    principal: str
    resource: str
    action: str
    allowed: bool
    reason: str
    policy_id: str | None = None
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# Default TypeDID profile id, mirroring TypeSec 0.10 "Murano"'s
# `TypeDidProfile::ed25519_x25519_chacha20()`.
TYPEDID_PROFILE = "ed25519-x25519-chacha20"


class TypeDidEnvelope(BaseModel):
    protocol: str = "querygraph.typedid.v1"
    conversation_id: str
    sender: str
    recipient: str
    action: str
    resource: str
    # Audit-safe attestation fields, mirroring the Rust port's adoption of
    # TypeSec 0.10 "Murano" `VerifiedTypeDidMessage::attestation()`: privacy
    # level, negotiated profile, and a digest binding the attestation to this
    # exact envelope — surfaced without revealing the payload.
    privacy: str = "secret"
    profile: str = TYPEDID_PROFILE
    content_type: str = "application/json"
    payload: dict[str, Any]
    payload_sha256: str
    signature: str
    envelope_digest: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        *,
        sender: DidDocument | str,
        recipient: DidDocument | str,
        action: str,
        resource: str,
        payload: dict[str, Any],
        conversation_id: str | None = None,
        content_type: str = "application/json",
        privacy: str = "secret",
        profile: str = TYPEDID_PROFILE,
    ) -> "TypeDidEnvelope":
        sender_id = sender.id if isinstance(sender, DidDocument) else sender
        recipient_id = recipient.id if isinstance(recipient, DidDocument) else recipient
        payload_hash = sha256_hex(_canonical(payload))
        conversation = conversation_id or f"qg:{payload_hash[:16]}"
        signature = sha256_hex(
            "\n".join(
                [
                    "querygraph-typedid-demo-signature-v1",
                    sender_id,
                    recipient_id,
                    action,
                    resource,
                    payload_hash,
                ]
            )
        )
        envelope_digest = sha256_hex(
            "\n".join(
                [
                    "querygraph-typedid-envelope-digest-v1",
                    conversation,
                    privacy,
                    profile,
                    signature,
                ]
            )
        )
        return cls(
            conversation_id=conversation,
            sender=sender_id,
            recipient=recipient_id,
            action=action,
            resource=resource,
            privacy=privacy,
            profile=profile,
            content_type=content_type,
            payload=payload,
            payload_sha256=payload_hash,
            signature=f"sha256:{signature}",
            envelope_digest=f"sha256:{envelope_digest}",
        )

    def verify_payload(self) -> bool:
        return self.payload_sha256 == sha256_hex(_canonical(self.payload))


class GovernedPrompt(BaseModel):
    question: str
    semantic_context: dict[str, Any]
    allowed_sources: list[str] = Field(default_factory=list)
    denied_sources: list[str] = Field(default_factory=list)
    receipts: list[AccessReceipt] = Field(default_factory=list)


class AgentResponse(BaseModel):
    agent: str
    status: Literal["allowed", "denied"]
    summary: str
    evidence: list[str] = Field(default_factory=list)
    redactions: list[str] = Field(default_factory=list)
    envelope: TypeDidEnvelope


class TypeDidAgent(BaseModel):
    name: str
    did: DidDocument
    capabilities: list[str] = Field(default_factory=list)

    @classmethod
    def new(cls, name: str, *, seed: str | None = None) -> "TypeDidAgent":
        did = DidDocument.new_oyd(seed or f"querygraph-agent:{name}", name)
        return cls(name=name, did=did, capabilities=[])

    def request(
        self,
        recipient: "TypeDidAgent",
        *,
        action: str,
        resource: str,
        payload: dict[str, Any],
    ) -> TypeDidEnvelope:
        return TypeDidEnvelope.create(
            sender=self.did,
            recipient=recipient.did,
            action=action,
            resource=resource,
            payload=payload,
        )

    def answer(
        self,
        request: TypeDidEnvelope,
        *,
        status: Literal["allowed", "denied"],
        summary: str,
        evidence: list[str] | None = None,
        redactions: list[str] | None = None,
    ) -> AgentResponse:
        payload = {
            "status": status,
            "summary": summary,
            "evidence": evidence or [],
            "redactions": redactions or [],
            "requestSha256": request.payload_sha256,
        }
        envelope = TypeDidEnvelope.create(
            sender=self.did,
            recipient=request.sender,
            action="respond",
            resource=request.resource,
            payload=payload,
            conversation_id=request.conversation_id,
        )
        return AgentResponse(
            agent=self.name,
            status=status,
            summary=summary,
            evidence=evidence or [],
            redactions=redactions or [],
            envelope=envelope,
        )


def evaluate_policy(
    *,
    principal: str,
    resource: str,
    action: Action,
    policy: Policy,
) -> AccessReceipt:
    allowed = policy.allows(principal, action)
    return AccessReceipt(
        principal=principal,
        resource=resource,
        action=action.iri(),
        allowed=allowed,
        reason="policy permitted action" if allowed else "policy denied action",
        policy_id=policy.id,
    )


def _canonical(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
