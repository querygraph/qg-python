from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from querygraph.codata import CodataOdrlClient
from querygraph.lakehouse import example_queries, register_audit, register_lakehouse
from querygraph.navigator import AiNavigator, NavigatorInput
from querygraph.qglake import build_python_qglake_story


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="querygraph", description="AI Navigator semantic layer CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    navigator = subparsers.add_parser(
        "navigator",
        help="Build a four-layer semantic bundle: Croissant, CDIF, DID, and ODRL.",
    )
    navigator.add_argument("--dataset-name", required=True)
    navigator.add_argument("--description", required=True)
    navigator.add_argument("--landing-page", required=True)
    navigator.add_argument("--data-url", required=True)
    navigator.add_argument("--creator", default="QueryGraph")
    navigator.add_argument("--agent-name", default="AI Navigator")

    anchor_url = subparsers.add_parser(
        "anchor-url", help="Reproduce the CODATA ODRL demo's URL-to-DID anchoring call."
    )
    anchor_url.add_argument("--url", default="https://querygraph.ai/resources/")
    anchor_url.add_argument("--endpoint", default="https://odrl.dev.codata.org")

    qglake_story = subparsers.add_parser(
        "qglake-story",
        help="Run the Python TypeDID/Pydantic QG Lakehouse agent story.",
    )
    qglake_story.add_argument("--pretty", action="store_true")

    lakehouse_register = subparsers.add_parser(
        "lakehouse-register",
        help="Register QueryGraph Sail lakehouse Parquet tables in a Spark Connect session.",
    )
    lakehouse_register.add_argument("--remote", default="sc://127.0.0.1:50051")
    lakehouse_register.add_argument(
        "--manifest", default=".querygraph/lakehouse/manifest/load-report.json"
    )
    lakehouse_register.add_argument("--warehouse", default="spark-warehouse")
    lakehouse_register.add_argument("--session-temp", action="store_true")

    audit_register = subparsers.add_parser(
        "audit-register",
        help="Register QueryGraph OpenLineage audit Parquet tables in a Spark Connect session.",
    )
    audit_register.add_argument("--remote", default="sc://127.0.0.1:50051")
    audit_register.add_argument("--warehouse", default="spark-warehouse")
    audit_register.add_argument("--session-temp", action="store_true")

    pyspark_examples = subparsers.add_parser(
        "pyspark-examples",
        help="Print example PySpark SQL queries for the registered Sail warehouse.",
    )
    pyspark_examples.add_argument("--scope", default="global_temp")

    args = parser.parse_args(argv)
    if args.command == "navigator":
        output = AiNavigator().build(
            NavigatorInput(
                dataset_name=args.dataset_name,
                description=args.description,
                landing_page=args.landing_page,
                data_url=args.data_url,
                creator=args.creator,
                agent_name=args.agent_name,
            )
        )
        print(json.dumps(output.bundle, indent=2))
        return 0

    if args.command == "qglake-story":
        indent = 2 if args.pretty else None
        print(json.dumps(build_python_qglake_story(), indent=indent))
        return 0

    if args.command == "lakehouse-register":
        rows = register_lakehouse(
            manifest=args.manifest,
            warehouse=args.warehouse,
            remote=args.remote,
            create_global_temp=not args.session_temp,
        )
        print(json.dumps(rows, indent=2))
        return 0

    if args.command == "audit-register":
        rows = register_audit(
            warehouse=args.warehouse,
            remote=args.remote,
            create_global_temp=not args.session_temp,
        )
        print(json.dumps(rows, indent=2))
        return 0

    if args.command == "pyspark-examples":
        print("\n".join(example_queries(args.scope)))
        return 0

    anchored = CodataOdrlClient(args.endpoint).create_did_from_url(args.url)
    print(json.dumps(_to_json(anchored), indent=2))
    return 0


def _to_json(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_json(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_to_json(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_json(item) for key, item in value.items()}
    return value
