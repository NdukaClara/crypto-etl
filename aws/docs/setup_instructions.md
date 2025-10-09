# 🧰 AWS Setup Instructions — Crypto ETL Pipeline

This document explains, **step by step**, how to set up the entire **Crypto ETL Pipeline** in AWS from scratch — including S3, Glue, Lambda, EventBridge, and SNS configuration.

By the end of this guide, your pipeline will automatically:

- Detect new CSV uploads to S3
- Trigger a Glue ETL job to transform them
- Store processed Parquet data in a dated folder structure
- Send an email notification when the job finishes or fails

---

## 🏗️ 1. Prerequisites

Before starting, ensure you have:

- An active AWS account
- IAM access to create and manage:
  - S3, Lambda, Glue, EventBridge, SNS
- AWS CLI (optional but helpful)
- A working S3 bucket (you’ll create this below)

---

## 🪣 2. Create an S3 Bucket

1. Go to **Amazon S3 → Create bucket**
2. Name it something like:
```

crypto-etl-bucket

```
3. Choose a region (e.g., `us-east-1`)
4. Leave defaults for permissions and encryption
5. Click **Create bucket**

### Folder structure inside S3
After setup, your bucket will look like this:

```

s3://crypto-etl-data-cc/
│
├── raw/              # Unprocessed CSVs uploaded manually
└── processed/        # Output of the Glue job (Parquet)

```

---

## ⚙️ 3. Create an AWS Glue Database

1. Go to **AWS Glue → Databases → Add database**
2. Name it:
```

crypto_db

```
3. Click **Create**

This database will later store the schema definitions for both raw and processed data (via crawlers).

---

## 🐍 4. Create the Glue Job (ETL Script)

1. Go to **AWS Glue → Jobs → Add job**
2. Name it:
```

crypto_transform_job

```
3. Choose an IAM role with **GlueFullAccess** and **S3 read/write** permissions  
*(You can reuse the same role for Lambda if desired.)*
4. Set the **Type** to “Spark”
5. Upload your ETL script:  
`aws/glue_jobs/crypto_transform_job.py`
6. Save and run once to validate configuration.

---

## 🧹 5. Create Glue Crawlers (for Athena)


### 🐝 a) Raw Data Crawler
1. Go to **AWS Glue → Crawlers → Add crawler**
2. Name it:
crypto_raw_crawler
3. Data source:
s3://crypto-etl-data-cc/raw/
4. Choose database:
crypto_db
5. Schedule: “On demand”
6. IAM role: Glue service role with S3 read access
7. Finish setup and run once.

This crawler maps your unprocessed CSV schema into `crypto_db` so Athena can query raw data directly.

---

### 🐝 b) Processed Data Crawler
1. Go to **AWS Glue → Crawlers → Add crawler**
2. Name it:
crypto_processed_crawler
3. Data source:
s3://crypto-etl-data-cc/processed/
4. Choose the same database:
crypto_db
5. Schedule: “On demand”
6. IAM role: same as above
7. Finish setup and run once.

✅ This crawler maps your processed Parquet data and automatically detects date partitions (e.g., `date=2025-10-06`).

---

## 🔔 6. Create an SNS Topic (Notifications)

1. Go to **Amazon SNS → Topics → Create topic**
2. Choose **Standard**
3. Name it:
```

crypto-etl-notifications

```
4. Copy the **Topic ARN** (you’ll use it in both Lambdas)
5. Under **Subscriptions**, click **Create subscription**
- Protocol: `Email`
- Endpoint: your email address
6. Confirm the subscription from your email inbox

---

## ⚡ 7. Create the First Lambda — Trigger ETL

**Purpose:** Detects file uploads in S3 and starts the Glue job.

1. Go to **AWS Lambda → Create function**
2. Name it:
```

crypto-trigger-lambda

```
3. Runtime: `Python 3.12` (or latest available)
4. Create or select an IAM role with:
- `AWSGlueServiceRole`
- `AmazonSNSFullAccess`
- `AmazonS3ReadOnlyAccess`
5. Paste the code from:
```

aws/lambda/trigger_lambda.py

```
6. In **Environment variables**, set:
```

GLUE_JOB_NAME = crypto_transform_job
SNS_TOPIC_ARN = arn:aws:sns:<region>:<account-id>:crypto-etl-notifications

```
7. Under **Configuration → Triggers → Add trigger**:
- Source: **S3**
- Bucket: `crypto-etl-bucket`
- Event type: **PUT (All object create events)**
- Prefix: `raw/`

✅ **This Lambda automatically starts the Glue job whenever a new CSV is uploaded to `raw/`.**

---

## 📊 8. Create the Second Lambda — Job Status Monitor

**Purpose:** Monitors Glue job completion and sends an SNS notification.

1. Go to **AWS Lambda → Create function**
2. Name it:
```

crypto-job-status-lambda

```
3. Runtime: `Python 3.12`
4. Assign an IAM role with:
- `AmazonSNSFullAccess`
- `AWSGlueConsoleFullAccess`
- `AmazonEventBridgeFullAccess`
5. Paste the code from:
```

aws/lambda/job_status_lambda.py

```
6. In **Environment variables**, set:
```

SNS_TOPIC_ARN = arn:aws:sns:<region>:<account-id>:crypto-etl-notifications

```

---

## 🕑 9. Create the EventBridge Rule

This rule connects the **Glue job state changes** to the **status Lambda**.

1. Go to **Amazon EventBridge → Rules → Create rule**
2. Name it:
```

crypto-glue-job-status

```
3. Type: **Rule with event pattern**
4. Event pattern JSON:

```json
{
  "source": ["aws.glue"],
  "detail-type": ["Glue Job State Change"],
  "detail": {
    "jobName": ["crypto_transform_job"]
  }
}
```

5. Target: **Lambda function**

   * Select `crypto-job-status-lambda`

✅ Now, whenever the Glue job **succeeds or fails**, this Lambda sends a status email via SNS.

---

## 🧠 10. Verify End-to-End Flow

1. Upload a CSV to S3:

   ```
   s3://crypto-etl-bucket/raw/btc_trades.csv
   ```
2. Monitor:

   * CloudWatch logs for both Lambdas
   * Glue job console for progress
3. Check processed output:

   ```
   s3://crypto-etl-bucket/processed/date=YYYY-MM-DD/
   ```
4. Open Athena → `crypto_db` → Run query:

   ```sql
   SELECT * FROM processed_data LIMIT 10;
   ```
5. Confirm that your **SNS email notification** was received.

---

## 🧩 11. Cleanup

When you’re done testing:

* Delete both Lambda functions
* Delete the EventBridge rule
* Delete Glue job and crawler
* Delete or empty your S3 bucket
* Unsubscribe from SNS notifications

---

## ✅ Summary

| Component        | Name                       | Purpose                    |
| ---------------- | -------------------------- | -------------------------- |
| S3 Bucket        | `crypto-etl-bucket`        | Store raw & processed data |
| Glue Database    | `crypto_db`                | Store schema for Athena    |
| Glue Job         | `crypto_transform_job`     | Transform CSV → Parquet    |
| Lambda 1         | `crypto-trigger-lambda`    | Starts Glue job on upload  |
| Lambda 2         | `crypto-job-status-lambda` | Sends SNS job updates      |
| EventBridge Rule | `crypto-job-status-rule`   | Monitors Glue job events   |
| SNS Topic        | `crypto-etl-notifications` | Email alerts               |
