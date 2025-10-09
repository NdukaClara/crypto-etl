# import pandas as pd

# # 1. Load the raw CSV
# df = pd.read_csv("data/trades.csv")

# print("✅ Raw data loaded")

# # 2. Basic cleaning / transformation
# df["time"] = pd.to_datetime(df["time"], unit="s", errors="coerce")
# df["amount"] = df["Price"] * df["Quantity"]

# # Rename columns for clarity
# df = df.rename(columns={
#     "Id": "trade_id",
#     "Time": "time",
#     "Price": "price",
#     "Quantity": "quantity",
#     "IsBuyerMaker": "is_buyer_maker",
#     "IsBestPriceMatch": "is_best_match"
# })

# # 3. Save cleaned version
# df.to_csv("data/trades_clean.csv", index=False)

# print("✅ Cleaned data saved to data/trades_clean.csv")
# print(df.head())
# print(f"Loaded rows: {len(df)}")
# print(df.shape)
# print(df.columns.tolist())

import pandas as pd
import boto3
import os
from config import S3_BUCKET, S3_PREFIX

# Load CSV
data_path = os.path.join("data", "trades.csv") 
df = pd.read_csv(data_path)

print("Data sample:")
print(df.head())

# Upload to S3
s3 = boto3.client("s3")

s3.upload_file(
    Filename=data_path,
    Bucket=S3_BUCKET,
    Key=f"{S3_PREFIX}trades.csv"
)

print(f"Uploaded {data_path} to s3://{S3_BUCKET}/{S3_PREFIX}trades.csv")
