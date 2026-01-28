import json
import re
import requests
import xml.etree.ElementTree as ET
import logging

from utils.output_s3 import store_grant_and_linking
from utils.schema_extract import get_grant_status_from_end_date, get_matched_funder_code

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_erc_id(text):
    m = re.search(r'(\d{6,})', text)
    return m.group(1) if m else None

# print(extract_erc_id("ERC 101089007"))

def get_eu_commision_grant(award_id: str, funder_name: str):
    ns = {'ns': 'http://cordis.europa.eu'}

    normalized_award_id = extract_erc_id(award_id)

    url = f"https://cordis.europa.eu/project/id/{normalized_award_id}?format=xml"

    response = requests.get(url, timeout=10)
    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = None
    status = "ACTIVE"

    funderCode = get_matched_funder_code(funder_name)
        
    if response.status_code == 200 and response != None:
        root = ET.fromstring(response.text)
       
        amount_elem = root.find('ns:totalCost', ns)
        startDate_elem = root.find('ns:startDate', ns)
        endDate_elem = root.find('ns:endDate', ns)
        grant_url = f"https://cordis.europa.eu/project/id/{normalized_award_id}"
        title_elem = root.find('ns:title', ns)
        
        amount = amount_elem.text if amount_elem is not None else None
        startDate = startDate_elem.text if startDate_elem is not None else None
        endDate = endDate_elem.text if endDate_elem is not None else None
        title = title_elem.text if title_elem is not None else None

        status = get_grant_status_from_end_date(endDate)

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

def lambda_handler(event, context):
    responses = {"grants": [], "linking": [], "errors": []}

    for record in event["Records"]:
        try:
            task = json.loads(record["body"])

            award_id = task.get("award_id")
            doi = task.get("doi")
            funder_name = task.get("funder_name")

            if not award_id:
                responses["errors"].append("Missing award_id")
                continue
            
            grant_result = get_eu_commision_grant(award_id, funder_name)

            stored = store_grant_and_linking(
                funder_name=funder_name,
                doi=doi,
                grant_result=grant_result,
            )

            responses["grants"].append(stored.get("grant_result"))
            responses["linking"].append(stored.get("grant_assets"))

        except Exception as e:
            logger.exception("Error processing record")
            print(e)
            responses["errors"].append(str(e))
    
    return {"statusCode": 200, "body": json.dumps(responses)}

