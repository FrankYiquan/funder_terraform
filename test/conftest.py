import sys
import os

# Project root (funder-infra/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# Add lambda-code folder so imports like nsf.handler work
sys.path.insert(0, os.path.join(ROOT, "lambda-code"))

# Add layers (simulate Lambda's /opt/python)
sys.path.insert(0, os.path.join(ROOT, "lambda-code/layers/shared_utils_layer/python"))
sys.path.insert(0, os.path.join(ROOT, "lambda-code/layers/requests_layer/python"))

# Set fake S3 environment variables
os.environ["GRANT_BUCKET"] = "brandeis-grants"
os.environ["LINKING_BUCKET"] = "asset-grant-linking"
