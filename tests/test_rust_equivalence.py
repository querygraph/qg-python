from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUST_ROOT = ROOT.parent / "qg-rust"


def test_navigator_cli_matches_rust_bundle_shape_and_content():
    args = [
        "navigator",
        "--dataset-name",
        "Hazard vocabulary",
        "--description",
        "Controlled vocabulary with multilingual technical terms",
        "--landing-page",
        "https://querygraph.ai/datasets/hazards",
        "--data-url",
        "https://querygraph.ai/datasets/hazards.csv",
        "--creator",
        "QueryGraph",
        "--agent-name",
        "AI Navigator",
    ]

    rust = json.loads(
        subprocess.check_output(["cargo", "run", "--quiet", "--", *args], cwd=RUST_ROOT)
    )
    python = json.loads(
        subprocess.check_output([sys.executable, "-m", "querygraph", *args], cwd=ROOT)
    )

    rust["generatedAt"] = "<normalized>"
    python["generatedAt"] = "<normalized>"
    assert python == rust
