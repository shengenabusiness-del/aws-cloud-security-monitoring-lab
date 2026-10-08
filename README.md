# AI-Powered AWS Cloud Security Monitoring & Automated Incident Analysis

## Overview

This project is a hands-on AWS cloud security monitoring system that automatically detects changes to EC2 Security Groups, evaluates their security risks, and generates AI-powered incident analysis using Amazon Bedrock and Anthropic Claude Haiku 4.5.

The goal was to build an event-driven security monitoring pipeline using native AWS services and integrate generative AI to assist with security investigations.

When a Security Group change occurs, the system automatically:

1. Detects the configuration change.
2. Captures the event through AWS CloudTrail.
3. Processes the event using AWS Lambda.
4. Assigns a severity level based on predefined security rules.
5. Sends the event details to Amazon Bedrock for AI analysis.
6. Generates a security risk assessment and recommended actions.
7. Delivers the alert and AI analysis through Amazon SNS.

The system operates automatically without requiring manual intervention.

## Architecture

![AWS Cloud Security Monitoring Architecture](AWS%20Cloud%20Security%20Monitoring%20Architecture%20%282%29.png)

**AI-Enhanced Architecture:**

```text
EC2 Security Group Change
           |
           v
     AWS CloudTrail
           |
           v
    Amazon EventBridge
           |
           v
       AWS Lambda
    (Python + Boto3)
           |
           v
    Severity Detection
           |
           v
     Amazon Bedrock
   (Claude Haiku 4.5)
           |
           v
    AI Security Analysis
           |
           v
       Amazon SNS
           |
           v
    Security Alert Email
```

The architecture combines traditional rule-based security detection with generative AI to provide additional context for security analysts.

## AWS Services Used

- **Amazon EC2** — Security Groups provide the network configurations being monitored.
- **AWS CloudTrail** — Records AWS API activity associated with Security Group changes.
- **Amazon EventBridge** — Detects monitored Security Group API events and invokes Lambda.
- **AWS Lambda** — Processes CloudTrail events, determines severity, and requests AI analysis.
- **Amazon Bedrock** — Provides managed access to the foundation model used for security analysis.
- **Anthropic Claude Haiku 4.5** — Generates contextual security risk assessments and remediation recommendations.
- **Amazon SNS** — Delivers automated security alerts through email.
- **Amazon CloudWatch** — Provides execution logs and troubleshooting information.
- **AWS IAM** — Manages permissions between AWS services.
- **Python / Boto3** — Implements event processing, AWS service integrations, and automation.

## Event Flow

1. A user modifies an EC2 Security Group.
2. AWS CloudTrail records the API activity.
3. Amazon EventBridge matches the event against the configured detection rule.
4. EventBridge invokes the `process-security-group-alert` Lambda function.
5. Lambda extracts relevant security information from the event.
6. Rule-based detection logic assigns a severity level.
7. Lambda invokes Claude Haiku 4.5 through Amazon Bedrock.
8. Claude analyzes the configuration change and generates a security assessment.
9. Lambda combines the event details, severity, and AI analysis into an alert.
10. Amazon SNS delivers the alert to the subscribed email address.

## Detection Logic

The EventBridge rule monitors the following EC2 API actions:

```text
AuthorizeSecurityGroupIngress
RevokeSecurityGroupIngress
AuthorizeSecurityGroupEgress
RevokeSecurityGroupEgress
```

These events represent changes to inbound or outbound Security Group rules.

The Lambda function extracts information including:

- API action
- Security Group ID
- AWS Region
- Identity associated with the change
- Event timestamp
- IP ranges
- Port ranges
- Network protocol

This information is used for both rule-based severity classification and AI analysis.

## Severity Classification

The system uses predefined detection rules to identify potentially dangerous network exposure.

### MEDIUM Severity

Standard Security Group configuration changes are classified as **MEDIUM** severity.

These events are monitored because even routine configuration changes can introduce security risks or violate organizational policies.

### HIGH Severity

An alert is classified as **HIGH** severity when a detected inbound rule exposes SSH (port 22) or RDP (port 3389) to:

```text
0.0.0.0/0
```

This represents remote administrative access being opened to the public internet.

The severity classification is determined by Python detection logic rather than the AI model.

## AI-Powered Security Analysis

One of the main enhancements to this project was integrating Amazon Bedrock into the existing detection pipeline.

After Lambda processes a Security Group event and assigns a severity level, it sends the relevant event information to Claude Haiku 4.5 through the Amazon Bedrock Converse API.

**Model:** Anthropic Claude Haiku 4.5

**Inference Profile:**

```text
global.anthropic.claude-haiku-4-5-20251001-v1:0
```

The model is prompted to act as a cloud security analyst and provide three components.

### 1. Security Risk

Explains why the detected Security Group change may present a security concern.

### 2. Potential Impact

Describes what could happen if the configuration is unsafe or left unaddressed.

### 3. Recommended Action

Provides investigation steps or remediation recommendations that a security analyst can review.

The AI analysis supplements the deterministic severity classification rather than replacing it.

### Example AI Analysis

For an inbound rule exposing SSH to the public internet, the AI may identify:

**Security Risk:** Public SSH access increases exposure to unauthorized connection attempts.

**Potential Impact:** An attacker could attempt credential-based attacks or exploit vulnerabilities in an exposed service.

**Recommended Action:** Verify that the rule is authorized, restrict access to trusted IP addresses, and investigate the associated CloudTrail activity.

*This is an illustrative example of the type of analysis generated by the model, not a verbatim test output.*

### Error Handling

The Lambda function includes exception handling for Amazon Bedrock requests.

If the AI service is unavailable or a model invocation fails, the system continues processing the event and sends the security alert with a message indicating that AI analysis was unavailable.

This prevents an AI service failure from stopping the core alerting workflow.

## Example Security Alert

```text
AWS CLOUD SECURITY ALERT

Severity: HIGH

Event:
Inbound security group rule added

AWS API Action:
AuthorizeSecurityGroupIngress

Security Group:
sg-example

Region:
us-east-2

Identity:
SecurityLabTestUser

Security Group Rule Details:
Protocol: tcp, Ports: 22-22, Source: 0.0.0.0/0

--------------------------------
AI SECURITY ANALYSIS
--------------------------------

Security Risk:
Public SSH access increases exposure to
unauthorized connection attempts.

Potential Impact:
An exposed administrative service could be
targeted by credential attacks or exploitation.

Recommended Action:
Confirm the change was authorized and restrict
SSH access to trusted IP addresses.

--------------------------------
RECOMMENDED ACTION
--------------------------------

Review the security group modification and verify
that the change was authorized and follows the
principle of least privilege.

---
AWS Cloud Security Monitoring & AI Analysis Lab
```

*Illustrative alert format. Actual AI-generated wording varies.*

## Testing

The system was validated through multiple testing stages.

### 1. Lambda Severity Detection Test

A simulated CloudTrail event representing SSH port 22 being opened to `0.0.0.0/0` was submitted directly to Lambda.

The function successfully:

- Parsed the security event.
- Identified the Security Group modification.
- Classified the event as HIGH severity.
- Generated an alert.
- Published the notification through Amazon SNS.

### 2. Amazon Bedrock Integration Test

A separate Lambda function was created to validate connectivity to Amazon Bedrock.

The test confirmed that:

- Lambda could invoke Claude Haiku 4.5.
- IAM permissions allowed model inference.
- The model could generate a contextual security assessment.
- The generated response could be retrieved programmatically.

After successful validation, the Bedrock integration was added to the primary security monitoring Lambda function.

### 3. AI-Enhanced Lambda Test

The updated Lambda function was tested using a simulated Security Group event representing public SSH exposure.

The function successfully:

- Classified the event as HIGH severity.
- Invoked Amazon Bedrock.
- Retrieved AI-generated security analysis.
- Included the analysis in the alert.
- Published the notification through Amazon SNS.

### 4. Real End-to-End Test

A real Security Group rule was modified in AWS to validate the complete automated workflow.

The temporary test rule used:

```text
Protocol: TCP
Port: 2222
Source: 192.0.2.10/32
```

The change triggered the monitoring pipeline automatically.

The system successfully:

- Detected the Security Group modification.
- Matched the event through EventBridge.
- Invoked the Lambda function.
- Classified the change as MEDIUM severity.
- Generated an AI-powered security assessment.
- Delivered the alert through Amazon SNS.

The temporary rule was removed after testing.

### Validation Result

```text
Real Security Group Change
            |
            v
       AWS CloudTrail
            |
            v
      Amazon EventBridge
            |
            v
         AWS Lambda
            |
            v
      Severity Analysis
            |
            v
       Amazon Bedrock
      (Claude Haiku 4.5)
            |
            v
      AI Risk Assessment
            |
            v
         Amazon SNS
            |
            v
      Email Notification
```

**Result: The complete AI-powered cloud security monitoring pipeline was successfully validated using a real AWS configuration change.**

## Test Evidence

The following screenshots document the implementation and testing of the security monitoring pipeline.

### 1. High-Severity Lambda Detection

A simulated CloudTrail event representing SSH exposure to `0.0.0.0/0` was processed by Lambda.

The function successfully classified the event as HIGH severity.

![Lambda High Severity Test](lambda-high-severity-test.png)

### 2. EventBridge Detection Rule

The EventBridge rule monitors CloudTrail events for EC2 Security Group ingress and egress modifications.

![EventBridge Detection Rule](eventbridge-detection-rule.png)

### 3. EventBridge to Lambda Integration

Matched events are forwarded to the `process-security-group-alert` Lambda function.

![EventBridge Lambda Target](eventbridge-lambda-target.png)

### 4. Security Alert Delivery

Amazon SNS delivers formatted security alerts through email.

![High Severity Email Alert](high-severity-email-alert.png)

### Additional AI Integration Evidence

The project was also validated using Amazon Bedrock and Claude Haiku 4.5.

Additional screenshots of the Bedrock integration and AI-generated email analysis can be included to document the enhanced workflow.

## Troubleshooting & Validation

During development, Amazon CloudWatch logs and AWS service metrics were used to troubleshoot and validate the system.

Testing included:

- EventBridge event matching
- EventBridge-to-Lambda invocation
- Lambda resource-based permissions
- IAM execution permissions
- Lambda event parsing
- SNS publishing
- Email subscriptions
- Amazon Bedrock model invocation
- Bedrock IAM authorization
- AI response processing
- End-to-end alert delivery

One integration challenge involved configuring the IAM permissions required for Amazon Bedrock model invocation.

After reviewing the authorization error and updating the Lambda execution role, the Bedrock request completed successfully.

Testing individual components before integrating them into the main workflow helped isolate and resolve configuration issues.

## Incident Response

Detection is only the first step of the security monitoring process.

This project includes an incident response runbook documenting how a security analyst should investigate and respond to Security Group alerts.

The runbook covers:

- Alert triage
- Security Group investigation
- CloudTrail identity validation
- Risk assessment
- Authorized versus unauthorized changes
- Remediation procedures
- Escalation considerations

AI-generated recommendations are intended to assist analysts. They should be reviewed and validated before remediation actions are taken.

📘 **[View the Security Group Incident Response Runbook](docs/incident-response.md)**

## Security Concepts Demonstrated

This project demonstrates practical experience with:

- AWS cloud security monitoring
- Detection engineering
- Event-driven security automation
- Serverless architecture
- AWS audit logging
- Network security
- IAM permissions
- Python and Boto3 automation
- Generative AI integration
- Amazon Bedrock model inference
- AI-assisted incident analysis
- Security alerting
- Incident response
- Cloud troubleshooting

## Future Improvements

Potential future enhancements include:

- Microsoft Teams or Slack notifications
- Automated Security Group remediation with approval controls
- Additional CloudTrail detections
- DynamoDB incident tracking
- Infrastructure as Code using Terraform
- Expanded severity scoring
- Security dashboards and metrics
- Improved event parsing and IPv6 detection
- AI analysis evaluation and monitoring
- Additional least-privilege IAM refinements

## Disclaimer

This project was created in a controlled AWS lab environment for educational and portfolio purposes.

AI-generated security analysis should be reviewed by a qualified analyst before making security decisions.
