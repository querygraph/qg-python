from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from querygraph.codata import CodataOdrlClient
from querygraph.navigator import AiNavigator, NavigatorInput


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
