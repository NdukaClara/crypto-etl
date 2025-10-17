# 💹 Crypto ETL Pipeline (AWS)

This project is a **fully automated crypto ETL pipeline** designed to extract, transform, and load cryptocurrency transaction data from **raw CSVs in S3** into a **processed analytics-ready format** — all orchestrated using AWS services.

The pipeline was built end-to-end to demonstrate how modern cloud-based data engineering workflows handle **data ingestion**, **processing**, and **event-driven automation** using native AWS tools like Glue, Lambda, and EventBridge.

---

## 🧠 Project Overview

The pipeline automatically:
- Detects when a new crypto CSV file is uploaded to an **S3 raw bucket**.
- Triggers an **AWS Glue job** via **Lambda**.
- Transforms and cleans the dataset using **PySpark** (within AWS Glue).
- Stores the processed data in **Parquet format**, partitioned by processing date, inside an S3 `processed/` folder.
- Sends **SNS email notifications** for job start, success, or failure.

This setup ensures a fully automated, scalable, and cost-efficient data pipeline suitable for analytical workloads like **crypto trade analysis**, **market trend modeling**, and **data warehousing**.

---

## 📂 Project Structure

crypto-etl/
│
├── data/ # Local raw CSVs (for initial testing)
│
├── scripts/ # Local ETL scripts
│ └── etl_local.py # Reads and transforms CSVs locally using pandas
│
├── aws/
│ ├── glue_jobs/
│ │ └── crypto_transform_job.py # Glue ETL script (PySpark-based)
│ │
│ ├── lambda/
│ │ ├── trigger_lambda.py # Starts Glue job on S3 upload
│ │ └── job_status_lambda.py# Monitors job completion via EventBridge
│ │
│ └── docs/
│ └── setup_instructions.md # Full AWS setup documentation
│
├── README.md # Project overview (this file)
│
└── .gitignore # Git ignore rules

---

## 🧩 AWS Architecture

**Services Used:**
- **Amazon S3** – Stores raw and processed crypto data.
- **AWS Glue** – Cleans and transforms uploaded CSV files using PySpark.
- **AWS Lambda** – Automates triggers and job monitoring.
- **Amazon SNS** – Sends email notifications on job status.
- **Amazon EventBridge** – Captures Glue job state changes.
- **Amazon Athena (Optional)** – Enables SQL queries on the processed Parquet data.

### 🔄 Workflow

+-------------+ +----------------+ +----------------+
| Upload CSV | ---> | Lambda Trigger | ---> | AWS Glue Job |
| to S3 | | (Start Job) | | (Transform) |
+-------------+ +----------------+ +----------------+
|
v
+--------------------+
| Processed Data (S3)|
+--------------------+
|
v
+-----------------------------+
| Lambda (Job Status Monitor) |
+-----------------------------+
|
v
+---------------+
| SNS Notification |
+---------------+


---

## ⚙️ Features

✅ **Fully Automated ETL:** The entire process triggers automatically on file upload.  
✅ **Serverless Architecture:** No servers to manage, pay only for usage.  
✅ **Schema-Aware Transformation:** Data is cleaned, renamed, and timestamped in Glue.  
✅ **Partitioned Output:** Processed files stored by date for easy querying.  
✅ **Email Notifications:** Glue job start, success, and error alerts via SNS.  
✅ **Athena Integration:** Enables quick SQL analysis on Parquet files.

---

## 🧰 Transformation Logic (in Glue)

The Glue script (`transform_data.py`) performs the following steps:

1. Reads raw CSV file from S3.
2. Renames `id` → `trade_id`.
3. Converts UNIX timestamps to readable datetime (`timestamp` column).
4. Removes duplicate trade records.
5. Adds metadata fields:
   - `source_file`
   - `processed_date`
6. Writes output as **Parquet** to:
s3://<your-bucket>/processed/date=YYYY-MM-DD/<filename>.parquet

🪣 Folder Layout in S3

s3://<your-bucket>/
│
├── raw/
│   └── btc_trades.csv
│
└── processed/
    └── date=2025-10-06/
        └── btc_trades.parquet

This structure keeps each day’s processed data neatly separated by date partitions.

---

## 🔔 Notifications

Two Lambda functions coordinate the automation:

| Function | Description |
|-----------|--------------|
| **Trigger Lambda** | Detects S3 upload → starts Glue job → sends SNS start notification. |
| **Status Lambda**  | Monitors Glue job state (via EventBridge) → sends success/failure alerts. |

---

## 🧠 Querying in Athena (Optional)

To explore your processed data in AWS Athena:

```sql
SELECT trade_id, price, timestamp
FROM crypto_db.processed_data
WHERE processed_date = '2025-10-06'
ORDER BY timestamp DESC;

```

🧾 Setup and Deployment

All setup steps (S3, Glue, Lambda, EventBridge, SNS, IAM roles, and Athena configuration)
are fully documented here:

📂 **[docs/setup_instructions.md](./docs/setup_instructions.md)**



⚠️ Important Notes

Strict Schema Enforcement:
The ETL script assumes consistent headers. If a new CSV has missing or mismatched columns (e.g., missing id or time), the Glue job may fail.
This design decision keeps transformations clean and consistent for analytics.
You can modify the transformation logic in transform_data.py to handle schema variations gracefully.

EventBridge Filtering:
The rule listens for all Glue job state changes (SUCCEEDED, FAILED, etc.) for accurate notifications.

SNS Notifications:
Ensure the SNS topic ARN used in both Lambdas is correct and subscribers have confirmed via email.


🧰 Local Testing

You can run local transformations using scripts/etl_local.py before uploading files to AWS for batch processing.


🧱 Requirements

AWS Account with permissions for S3, Glue, Lambda, SNS, and EventBridge.

Python 3.10+ for local script testing.

AWS Glue 4.0 or newer.

Active SNS subscription (verify email to receive notifications).


## 🧾 License

This project is publicly available for learning and demonstration purposes only.  
All rights are reserved — reuse, modification, or redistribution of any part of this codebase is **not permitted** without explicit permission from the author.


✨ Author’s Note

This project showcases how to design a real-world, event-driven data engineering pipeline in AWS —
from ingestion to transformation to notification — all automated and serverless.

Whether you’re learning AWS data engineering or building your own cloud-based ETL,
this project serves as a clear, reproducible reference.


⚠️ Before deploying, replace placeholders like <your-s3-bucket> and <your-sns-topic-arn> with your actual AWS resource names.


✨ Author

Clara Nduka
Software Engineer
📫 ndukaclara@gmail.com
💼 linkedin.com/in/clara-nduka