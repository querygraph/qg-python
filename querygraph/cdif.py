from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from querygraph.croissant import CroissantDataset


class CdifProfile(Enum):
    DISCOVERY = "https://cdif.codata.org/profile/discovery"
    DATA_ACCESS = "https://cdif.codata.org/profile/data-access"
    CONTROLLED_VOCABULARIES = "https://cdif.codata.org/profile/controlled-vocabularies"
    DATA_INTEGRATION = "https://cdif.codata.org/profile/data-integration"
    UNIVERSALS = "https://cdif.codata.org/profile/universals"

    def iri(self) -> str:
        return self.value


@dataclass(frozen=True)
class CdifResource:
    dataset_id: str
    profiles: list[CdifProfile]
    landing_page: str
    access_service: str
    temporal_coverage: str | None = None
    spatial_coverage: str | None = None
    units: list[str] = field(default_factory=list)
    vocabularies: list[str] = field(default_factory=list)

    @classmethod
    def from_croissant(
        cls, dataset: CroissantDataset, landing_page: str, access_service: str
    ) -> "CdifResource":
        vocabularies = [
            field.semantic_type_value
            for record_set in dataset.record_sets
            for field in record_set.fields
            if field.semantic_type_value is not None
        ]
        return cls(
            dataset_id=dataset.id,
            profiles=[
                CdifProfile.DISCOVERY,
                CdifProfile.DATA_ACCESS,
                CdifProfile.CONTROLLED_VOCABULARIES,
                CdifProfile.DATA_INTEGRATION,
                CdifProfile.UNIVERSALS,
            ],
            landing_page=landing_page,
            access_service=access_service,
            vocabularies=vocabularies,
        )

    def to_json_ld(self) -> dict:
        return {
            "@type": "dcat:Dataset",
            "@id": self.dataset_id,
            "cdif:profile": [profile.iri() for profile in self.profiles],
            "dcat:landingPage": self.landing_page,
            "dcat:accessService": {
                "@type": "dcat:DataService",
                "endpointURL": self.access_service,
            },
            "dct:temporal": self.temporal_coverage,
            "dct:spatial": self.spatial_coverage,
            "cdif:unit": self.units,
            "cdif:controlledVocabulary": self.vocabularies,
        }
