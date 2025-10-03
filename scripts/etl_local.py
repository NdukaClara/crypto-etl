import pandas as pd

# 1. Load the raw CSV
df = pd.read_csv("data/trades.csv")

print("✅ Raw data loaded")

# 2. Basic cleaning / transformation
df["time"] = pd.to_datetime(df["time"], unit="s", errors="coerce")
df["amount"] = df["Price"] * df["Quantity"]

# Rename columns for clarity
df = df.rename(columns={
    "Id": "trade_id",
    "Time": "time",
    "Price": "price",
    "Quantity": "quantity",
    "IsBuyerMaker": "is_buyer_maker",
    "IsBestPriceMatch": "is_best_match"
})

# 3. Save cleaned version
df.to_csv("data/trades_clean.csv", index=False)

print("✅ Cleaned data saved to data/trades_clean.csv")
print(df.head())
print(f"Loaded rows: {len(df)}")
print(df.shape)
print(df.columns.tolist())
