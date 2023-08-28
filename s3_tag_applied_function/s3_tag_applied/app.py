import os
from unicodedata import name
import boto3 

TAGS = os.environ['TAGS'].split(',')
COMPANY_NAME = os.environ['COMPANY_NAME']
CROSS_ACCOUNT_ROLE = os.environ['CROSS_ACCOUNT_ROLE']


sts_client = boto3.client('sts')


def lambda_handler(event, _context):
    tags =  event['detail']['requestParameters']['Tagging']['TagSet']['Tag']

    if not isinstance(tags, list):
        tags = [tags]

    for tag in tags:
        key = tag['Key']
        if key in TAGS:
            create_incident(event, key)


def create_incident(event, tag):
    print(f"Creating SOC incident: found '{tag}'.")

    print(event)

    detail = event['detail']
    finding_id = event['id']
    timestamp = event['time']

    account_id = detail['resources'][0]['accountId']
    region = detail['awsRegion']
    bucket_name = detail['requestParameters']['bucketName']

    severity = 'CRITICAL'
    incident_domain = 'INFRA'
    ticket_destination = 'SOC'
    namespace = 'S3-tagged-public'
    remediation_text = 'Please contact the team to verify that the use case is legitimate.'
    remediation_url = 'https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-standards-fsbp-controls.html#fsbp-s3-2'

    title = f"The tag '{tag}' was applied to the S3 bucket '{bucket_name}'"

    description = f'''\
{severity} INCIDENT in account {account_id}, region {region}:

The bucket '{bucket_name}' has been been tagged '{tag}.'

Setting this tag prevents automation from closing the bucket for public access.
It doesn't open the bucket for public access per se; this must be done by the
developers themselves.
'''


    finding = {
        "SchemaVersion": "2018-10-08",
        "Id": finding_id,
        "ProductArn": f"arn:aws:securityhub:{region}:{account_id}:product/{account_id}/default",
        "GeneratorId": title,
        "AwsAccountId": account_id,
        "Types": [
            f"Software and Configuration Checks/S3/{namespace}",
        ],
        "CreatedAt": timestamp,
        "UpdatedAt": timestamp,
        "Severity": {
            "Label": severity
        },
        "Title": title,
        "Description": description,
        "Remediation": {
            "Recommendation": {
                "Text": remediation_text,
                "Url": remediation_url
            }
        },
        "Resources": [
            {
                "Type": "AwsAccountId",
                "Id": account_id,
                "Region": region,
            },
        ],
        "ProductFields": {
            "aws/securityhub/FindingId": f"arn:aws:securityhub:{region}:{account_id}:product/{account_id}/default/{finding_id}",
            "aws/securityhub/ProductName": "Default",
            "aws/securityhub/CompanyName": COMPANY_NAME,
            "TicketDestination": ticket_destination,
            "IncidentDomain": incident_domain
        },
        "VerificationState": "TRUE_POSITIVE",
        "Workflow": {
            "Status": "NEW"
        },
        "RecordState": "ACTIVE"
    }

    print(f"Creating {severity} incident for {incident_domain} S3 bucket event '{title}'...")
    client = get_client('securityhub', account_id, region)
    response = client.batch_import_findings(Findings=[finding])
    if response['FailedCount'] != 0:
        print(f"The finding failed to import: '{response['FailedFindings']}'")
    else:
        print("Finding imported successfully.")

    return True
   

def get_client(client_type, account_id, region, role=CROSS_ACCOUNT_ROLE):
    other_session = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/{role}",
        RoleSessionName=f"public_s3_tag_applied_session_{account_id}"
    )
    access_key = other_session['Credentials']['AccessKeyId']
    secret_key = other_session['Credentials']['SecretAccessKey']
    session_token = other_session['Credentials']['SessionToken']
    return boto3.client(
        client_type,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        region_name=region
    )
