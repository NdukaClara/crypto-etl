import json
import boto3
import os

glue = boto3.client('glue')
sns = boto3.client('sns')

SNS_TOPIC_ARN = "arn:aws:sns:REGION:ACCOUNT_ID:YOUR_TOPIC"
GLUE_JOB_NAME = "crypto_transform_job"

def lambda_handler(event, context):
    try:
        # Get S3 object info
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        file_name = record['s3']['object']['key']

        print(f"📁 New file uploaded: s3://{bucket_name}/{file_name}")

        # --- ✅ Concurrency check ---
        running_jobs = glue.get_job_runs(JobName=GLUE_JOB_NAME, MaxResults=1)['JobRuns']
        if running_jobs and running_jobs[0]['JobRunState'] == 'RUNNING':
            message = f"⚠️ Glue job '{GLUE_JOB_NAME}' is already running. Skipping trigger for: {file_name}"
            print(message)
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Crypto ETL Job Skipped (Already Running)",
                Message=message
            )
            return {'statusCode': 200, 'body': json.dumps('Job skipped')}

        # --- ✅ Add optional job arguments ---
        job_args = {
            '--SOURCE_BUCKET': bucket_name,
            '--SOURCE_FILE': file_name
        }

        # --- ✅ Start Glue job ---
        response = glue.start_job_run(
            JobName=GLUE_JOB_NAME,
            Arguments=job_args
        )

        job_run_id = response['JobRunId']
        message = (
            f"✅ Glue ETL job started successfully!\n"
            f"Job ID: {job_run_id}\n"
            f"File: s3://{bucket_name}/{file_name}"
        )
        print(message)

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Crypto ETL Job Started",
            Message=message
        )

        return {'statusCode': 200, 'body': json.dumps('Glue job started successfully')}

    except Exception as e:
        error_message = f"❌ Failed to start Glue job: {str(e)}"
        print(error_message)
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Crypto ETL Job Failed",
            Message=error_message
        )
        raise e
