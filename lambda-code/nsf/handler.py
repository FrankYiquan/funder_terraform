import json
import re
import requests
from datetime import datetime
import logging

from utils.output_s3 import store_grant_and_linking

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ----------------------------
# Award ID normalization logic
# ----------------------------
def clean_award_id(award_id):
    text = str(award_id).strip()

    # Find digit sequences
    digit_groups = re.findall(r"\d+", text)

    if not digit_groups:
        return []

    # Detect multiple award codes e.g. "DMR-1809762 CBET-1916877"
    codes = re.findall(r"[A-Za-z]+[- ]*\d+", text)
    if len(codes) > 1:
        return [
            re.findall(r"\d+", code)[0]
            for code in codes
            if len(re.findall(r"\d+", code)[0]) > 3
        ]

    # Single award → combine digits like PHY17-48958 → "1748958"
    return ["".join(digit_groups)]


# ----------------------------
# NSF API fetch
# ----------------------------
def get_award_from_NSF(award_id: str) -> str:
    normalized = award_id.strip()
    url = f"http://api.nsf.gov/services/v1/awards/{normalized}.json"

    response = requests.get(url)
    data = response.json()

    amount = None
    startDate = None
    endDate = None
    title = None
    grant_url = None
    funderCode = "41___NATIONAL_SCIENCE_FOUNDATION_(ALEXANDRIA)"
    status = "ACTIVE"

    if response.status_code == 200 and data.get("response", {}).get("metadata", {}).get("totalCount", 0) > 0:
        award = data["response"]["award"][0]
        amount = award.get("fundsObligatedAmt")

        # Parse dates
        project_start = award.get("startDate")
        if project_start:
            startDate = datetime.strptime(project_start, "%m/%d/%Y").strftime("%Y-%m-%d")

        project_end = award.get("expDate")
        if project_end:
            endDate = datetime.strptime(project_end, "%m/%d/%Y").strftime("%Y-%m-%d")
            if datetime.strptime(project_end, "%m/%d/%Y").date() < datetime.now().date():
                status = "HISTORY"

        title = award.get("title")
        award_id = award.get("id")
        grant_url = f"https://www.nsf.gov/awardsearch/show-award?AWD_ID={award_id}"

    result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result


# ----------------------------
# Lambda entrypoint
# ----------------------------
def lambda_handler(event, context):
    responses = {"grants": [], "linking": [], "errors": []}

    for record in event["Records"]:
        try:
            task = json.loads(record["body"])

            award_id = task.get("award_id")
            doi = task.get("doi")

            if not award_id:
                responses["errors"].append("Missing award_id")
                continue

            # Extract clean ID(s)
            normalized_ids = clean_award_id(award_id)

            for nid in normalized_ids:
                grant_result = get_award_from_NSF(nid)

                stored = store_grant_and_linking(
                    funder_name="National Science Foundation",
                    doi=doi,
                    grant_result=grant_result,
                )

                responses["grants"].append(stored["grant_key"])
                responses["linking"].append(stored["linking_key"])

        except Exception as e:
            logger.exception("Error processing record")
            responses["errors"].append(str(e))

    return {"statusCode": 200, "body": json.dumps(responses)}
