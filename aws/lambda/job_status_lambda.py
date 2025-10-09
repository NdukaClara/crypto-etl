import json
import boto3
import os

sns = boto3.client("sns")

# Same SNS topic used earlier for notifications
SNS_TOPIC_ARN = "arn:aws:sns:REGION:ACCOUNT_ID:YOUR_TOPIC"

def lambda_handler(event, context):
    print("🔔 Received EventBridge event:")
    print(json.dumps(event, indent=2))

    try:
        # Extract job details from event
        detail = event.get("detail", {})
        job_name = detail.get("jobName", "UnknownJob")
        job_run_id = detail.get("jobRunId", "UnknownRun")
        state = detail.get("state", "UNKNOWN")

        message = (
            f"Glue job update:\n\n"
            f"Job Name: {job_name}\n"
            f"Run ID: {job_run_id}\n"
            f"Status: {state}\n"
        )

        # Add success/failure emoji for clarity
        if state == "SUCCEEDED":
            subject = f"✅ Glue Job Succeeded: {job_name}"
        elif state == "FAILED":
            subject = f"❌ Glue Job Failed: {job_name}"
        else:
            subject = f"⚙️ Glue Job Update: {job_name}"

        # Publish to SNS topic
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )

        print("✅ Notification sent successfully.")
        return {"statusCode": 200, "body": json.dumps("Notification sent!")}

    except Exception as e:
        print(f"❌ Error processing event: {e}")
        raise e
