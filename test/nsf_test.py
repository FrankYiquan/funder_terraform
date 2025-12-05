import json
from unittest.mock import patch

from nsf.handler import lambda_handler   


# ----------------------------
# Fake event
# ----------------------------
fake_event = {
    "Records": [
        {
            "body": json.dumps({
                "award_id": "DMR-1809762 CBET-1916877 CMMT-2026834 BSF-2016188",
                "doi": "10.1063/5.0202872"
            })
        }
    ]
}

# ----------------------------
# Patch S3 put_object
# ----------------------------
@patch("utils.output_s3.s3.put_object")
def test_lambda(mock_put_object):

    mock_put_object.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }

    result = lambda_handler(fake_event, None)
    parsed_body = json.loads(result["body"])

    # Print useful debug info
    print("\n=== Lambda Output (grant keys) ===")
    print(parsed_body["grants"])
    
    print("\n=== Number of S3 Calls ===")
    print(mock_put_object.call_count)

    # Inspect each call
    for i, call in enumerate(mock_put_object.call_args_list, start=1):
        print(f"\n--- S3 Call #{i} ---")

        bucket = call.kwargs["Bucket"]
        key = call.kwargs["Key"]
        content_type = call.kwargs.get("ContentType")
        body = call.kwargs["Body"]

        print(f"Bucket:       {bucket}")
        print(f"Key:          {key}")
        print(f"Content-Type: {content_type}")
        print("Body:")
        print(body)

