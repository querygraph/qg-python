from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from querygraph.croissant import CroissantDataset


class OsiDialectExpression(BaseModel):
    dialect: str
    expression: str


class OsiExpression(BaseModel):
    dialects: list[OsiDialectExpression] = Field(default_factory=list)


class OsiField(BaseModel):
    name: str
    description: str | None = None
    semantic_type: str | None = None
    expression: OsiExpression | None = None


class OsiDataset(BaseModel):
    name: str
    source: str
    description: str | None = None
    ai_context: str | None = None
    fields: list[OsiField] = Field(default_factory=list)


class OsiMetric(BaseModel):
    name: str
    expression: OsiExpression
    description: str | None = None
    ai_context: str | None = None


class OsiOntologyTerm(BaseModel):
    id: str
    label: str
    source: str | None = None


class OsiSemanticModel(BaseModel):
    name: str
    description: str | None = None
    ai_context: str | None = None
    datasets: list[OsiDataset] = Field(default_factory=list)
    metrics: list[OsiMetric] = Field(default_factory=list)
    ontology_terms: list[OsiOntologyTerm] = Field(default_factory=list)


class OsiDocument(BaseModel):
    version: str = "0.2.0.dev0"
    semantic_model: OsiSemanticModel

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "OsiDocument":
        return cls.model_validate(value)

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> "OsiDocument":
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - exercised by users.
            raise RuntimeError("Install PyYAML to load OSI YAML files.") from exc
        return cls.from_mapping(yaml.safe_load(Path(path).read_text()))

    @classmethod
    def from_croissant(
        cls,
        dataset: CroissantDataset,
        *,
        model_name: str | None = None,
        sail_schema: str = "qg_lakehouse",
    ) -> "OsiDocument":
        fields = [
            OsiField(
                name=field.name,
                description=field.description,
                semantic_type=field.semantic_type_value,
                expression=OsiExpression(
                    dialects=[
                        OsiDialectExpression(
                            dialect="SAIL_SQL",
                            expression=f"`{field.name}`",
                        )
                    ]
                ),
            )
            for record_set in dataset.record_sets
            for field in record_set.fields
        ]
        terms = [
            OsiOntologyTerm(
                id=field.semantic_type_value,
                label=field.name,
                source="semantic-croissant",
            )
            for record_set in dataset.record_sets
            for field in record_set.fields
            if field.semantic_type_value
        ]
        safe_name = _safe_sql_name(dataset.name)
        return cls(
            semantic_model=OsiSemanticModel(
                name=model_name or f"{safe_name}_semantic_model",
                description=f"OSI model derived from Semantic Croissant dataset {dataset.name}.",
                ai_context=(
                    "Resolve user intent to ontology terms, then map those terms "
                    "to Croissant fields and governed Sail columns."
                ),
                datasets=[
                    OsiDataset(
                        name=safe_name,
                        source=f"sail.{sail_schema}.{safe_name}",
                        description=dataset.description,
                        ai_context=(
                            f"Dataset {dataset.name} has {len(dataset.files)} file(s) "
                            f"and {len(fields)} semantic field(s)."
                        ),
                        fields=fields,
                    )
                ],
                metrics=[
                    OsiMetric(
                        name="row_count",
                        description="Count of governed rows available in Sail.",
                        expression=OsiExpression(
                            dialects=[
                                OsiDialectExpression(
                                    dialect="SAIL_SQL",
                                    expression="COUNT(*)",
                                )
                            ]
                        ),
                        ai_context="Use this metric to verify loaded table scale.",
                    )
                ],
                ontology_terms=terms,
            )
        )

    def to_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)


def _safe_sql_name(name: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "_" for ch in name)
    out = "_".join(part for part in out.split("_") if part)
    return out or "dataset"
