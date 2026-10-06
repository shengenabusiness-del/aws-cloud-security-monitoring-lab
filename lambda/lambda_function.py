import json
import boto3
import os

sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):

    detail = event.get("detail", {})

    event_name = detail.get("eventName", "Unknown")
    event_time = detail.get("eventTime", event.get("time", "Unknown"))
    region = detail.get("awsRegion", event.get("region", "Unknown"))

    user_identity = detail.get("userIdentity", {})
    username = (
        user_identity.get("sessionContext", {})
        .get("sessionIssuer", {})
        .get("userName", "Unknown")
    )

    request_parameters = detail.get("requestParameters", {})
    group_id = request_parameters.get("groupId", "Unknown")

    # Translate AWS API names into readable descriptions
    event_descriptions = {
        "AuthorizeSecurityGroupIngress": "Inbound security group rule added",
        "RevokeSecurityGroupIngress": "Inbound security group rule removed",
        "AuthorizeSecurityGroupEgress": "Outbound security group rule added",
        "RevokeSecurityGroupEgress": "Outbound security group rule removed"
    }

    description = event_descriptions.get(
        event_name,
        "Security group configuration changed"
    )

    severity = "MEDIUM"

    # Look for potentially dangerous public access
    permissions = request_parameters.get("ipPermissions", {}).get("items", [])

    for permission in permissions:

        from_port = permission.get("fromPort")
        to_port = permission.get("toPort")

        ip_ranges = permission.get("ipRanges", {}).get("items", [])

        for ip_range in ip_ranges:

            cidr = ip_range.get("cidrIp", "")

            # Public SSH or RDP exposure
            if cidr == "0.0.0.0/0" and (
                from_port in [22, 3389] or
                to_port in [22, 3389]
            ):
                severity = "HIGH"

    message = f"""
AWS CLOUD SECURITY ALERT

Severity: {severity}

Event:
{description}

AWS API Action:
{event_name}

Security Group:
{group_id}

Region:
{region}

Identity:
{username}

Event Time:
{event_time}

Recommended Action:
Review the security group modification and verify that the change
was authorized and follows the principle of least privilege.

---
AWS Cloud Security Monitoring Lab
"""

    print(json.dumps(event))
    print(message)

    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"[{severity}] AWS Security Group Alert",
        Message=message
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Security alert processed successfully",
            "snsMessageId": response["MessageId"]
        })
    }












    
