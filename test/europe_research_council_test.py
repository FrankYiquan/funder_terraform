import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock
import importlib.util


def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main():
    # This file lives in funder-Terraform/test/, so parents[1] is funder-Terraform/
    repo_root = Path(__file__).resolve().parents[1]

    # ---- Set env vars BEFORE importing handler (output_s3 reads these at import time) ----
    os.environ.setdefault("GRANT_BUCKET", "fake-grant-bucket")
    os.environ.setdefault("LINKING_BUCKET", "fake-linking-bucket")

    # ---- Make Lambda layers importable locally ----
    shared_utils_path = repo_root / "lambda-code" / "layers" / "shared_utils_layer" / "python"
    requests_layer_path = repo_root / "lambda-code" / "layers" / "requests_layer" / "python"
    sys.path.insert(0, str(shared_utils_path))
    sys.path.insert(0, str(requests_layer_path))

    # ---- Fake boto3 so `import boto3` doesn't fail locally ----
    fake_boto3 = MagicMock()
    fake_boto3.client.return_value = MagicMock()
    sys.modules["boto3"] = fake_boto3

    handler = load_module_from_path(
        "erc_handler",
        repo_root / "lambda-code" / "European_Research_Council" / "handler.py",
    )

    # ---- Fake SQS event ----
    fake_event = {
        "Records": [
            {
                "body": json.dumps({
                    "award_id": "240672",
                    "doi": "10.1093/mnras/stz272",
                    "funder_name": "European Research Council",
                })
            }
        ]
    }

    result = handler.lambda_handler(fake_event, None)

    print("\n=== Grant XML ===")
    body = json.loads(result["body"])
    print(body["grants"][0])   
    print("\n=== Linking JSON ===")
    print(body["linking"][0])
    
if __name__ == "__main__":
    main()
