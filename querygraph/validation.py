from __future__ import annotations

from typing import Any


def validate_croissant(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require(value, "@type", "cr:Dataset", errors)
    _require_present(value, "@id", errors)
    _require_present(value, "recordSet", errors)
    return errors


def validate_cdif(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require(value, "@type", "dcat:Dataset", errors)
    _require_present(value, "cdif:profile", errors)
    _require_present(value, "dct:accessRights", errors)
    _require_present(value, "cdif:dataElement", errors)
    return errors


def validate_openlineage(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require_present(value, "eventType", errors)
    _require_present(value, "eventTime", errors)
    _require_present(value, "run", errors)
    _require_present(value, "job", errors)
    _require_present(value, "inputs", errors)
    _require_present(value, "outputs", errors)
    return errors


def _require(value: dict[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    if value.get(key) != expected:
        errors.append(f"{key} must be {expected!r}")


def _require_present(value: dict[str, Any], key: str, errors: list[str]) -> None:
    if key not in value or value[key] is None:
        errors.append(f"{key} is required")
