import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, when, timestamp_seconds, date_format, lit
from datetime import datetime

# --- Get arguments passed from Lambda ---
args = getResolvedOptions(sys.argv, ["JOB_NAME", "SOURCE_BUCKET", "SOURCE_FILE"])
source_bucket = args["SOURCE_BUCKET"]
source_file = args["SOURCE_FILE"]

input_path = f"s3://{source_bucket}/{source_file}"
print(f"🔍 Processing file: {input_path}")

# --- Initialize Glue job ---
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# --- Load raw CSV from S3 ---
df = spark.read.option("header", True).csv(input_path)

# --- Add metadata columns ---
today_str = datetime.now().strftime("%Y-%m-%d")
df = df.withColumn("source_file", lit(source_file)) \
       .withColumn("processed_date", lit(today_str))

# --- Transformations ---
df_cleaned = (
    df.withColumnRenamed("id", "trade_id")
      # Ensure 'time' is numeric
      .withColumn("time_num", col("time").cast("double"))
      # Convert to TimestampType with milliseconds precision
      .withColumn(
          "timestamp",
          when(col("time_num") > 1e12, timestamp_seconds(col("time_num") / 1000))
          .otherwise(timestamp_seconds(col("time_num")))
      )
      .dropDuplicates(["trade_id"])
      .orderBy(col("timestamp"))
      .drop("time_num")
)

# --- Define output path ---
file_base = source_file.split("/")[-1].replace(".csv", "")
output_path = f"s3://{source_bucket}/processed/date={today_str}/{file_base}/"
print(f"📦 Writing processed data to: {output_path}")

# --- Write DataFrame directly as Parquet ---
df_cleaned.write.mode("overwrite").parquet(output_path)

print("✅ Transformation and upload complete.")


# import sys
# from awsglue.transforms import *
# from awsglue.utils import getResolvedOptions
# from pyspark.context import SparkContext
# from awsglue.context import GlueContext
# from awsglue.job import Job
# from awsglue.dynamicframe import DynamicFrame
# from pyspark.sql.functions import col, from_unixtime

# # Get job arguments from Lambda
# args = getResolvedOptions(sys.argv, ["JOB_NAME", "SOURCE_BUCKET", "SOURCE_FILE"])
# source_bucket = args["SOURCE_BUCKET"]
# source_file = args["SOURCE_FILE"]

# sc = SparkContext()
# glueContext = GlueContext(sc)
# spark = glueContext.spark_session
# job = Job(glueContext)
# job.init(args["JOB_NAME"], args)

# # --- ✅ Read only the specific uploaded CSV ---
# input_path = f"s3://{source_bucket}/{source_file}"
# print(f"Reading data from: {input_path}")

# raw_data = (
#     spark.read
#     .option("header", True)
#     .csv(input_path)
# )

# # --- ✅ Transform data ---
# df_cleaned = (
#     raw_data.withColumnRenamed("id", "trade_id")
#             .withColumn("timestamp", from_unixtime(col("time")))
#             .dropDuplicates(["trade_id"])
#             .orderBy(col("timestamp"))
# )

# # --- ✅ Write transformed data to 'processed/' folder ---
# output_path = f"s3://{source_bucket}/processed/{source_file.replace('.csv', '.parquet')}"
# print(f"Writing processed data to: {output_path}")

# df_cleaned.write.mode("overwrite").parquet(output_path)

# print("✅ Transformation complete.")
# job.commit()
