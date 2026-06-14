from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel, Field

from querygraph.typedid import AgentResponse, GovernedPrompt, TypeDidAgent


class TypeDidAgentRun(BaseModel):
    supervisor: TypeDidAgent
    specialists: list[TypeDidAgent]
    prompt: GovernedPrompt
    responses: list[AgentResponse] = Field(default_factory=list)

    def aggregate(self) -> dict[str, Any]:
        allowed = [response for response in self.responses if response.status == "allowed"]
        denied = [response for response in self.responses if response.status == "denied"]
        return {
            "supervisor": self.supervisor.name,
            "question": self.prompt.question,
            "allowedSummaries": [response.summary for response in allowed],
            "denials": [response.summary for response in denied],
            "evidenceHashes": [
                response.envelope.payload_sha256 for response in self.responses
            ],
        }


def deterministic_specialist(
    agent: TypeDidAgent,
    *,
    summary: str,
    status: str = "allowed",
    evidence: list[str] | None = None,
    redactions: list[str] | None = None,
) -> Callable[[dict[str, Any]], AgentResponse]:
    def invoke(payload: dict[str, Any]) -> AgentResponse:
        supervisor = TypeDidAgent.new("SupervisorAgent")
        request = supervisor.request(
            agent,
            action=payload.get("action", "summarize"),
            resource=payload.get("resource", "qg_lakehouse"),
            payload=payload,
        )
        return agent.answer(
            request,
            status="allowed" if status == "allowed" else "denied",
            summary=summary,
            evidence=evidence or [payload.get("resource", "qg_lakehouse")],
            redactions=redactions or [],
        )

    return invoke


class TypeDidLangChainToolAdapter:
    """Small adapter that exposes a TypeDID agent as a LangChain StructuredTool."""

    def __init__(
        self,
        agent: TypeDidAgent,
        handler: Callable[[dict[str, Any]], AgentResponse],
    ) -> None:
        self.agent = agent
        self.handler = handler

    def as_tool(self):
        try:
            from langchain_core.tools import StructuredTool
        except ImportError as exc:  # pragma: no cover - depends on optional extra.
            raise RuntimeError(
                "Install querygraph[agents] to use LangChain tool adapters."
            ) from exc

        def run(question: str, resource: str = "qg_lakehouse") -> dict[str, Any]:
            response = self.handler(
                {"question": question, "resource": resource, "action": "summarize"}
            )
            return response.model_dump(mode="json")

        return StructuredTool.from_function(
            func=run,
            name=self.agent.name,
            description=(
                f"Governed TypeDID tool for {self.agent.name}; returns a signed "
                "summary or denial."
            ),
        )
