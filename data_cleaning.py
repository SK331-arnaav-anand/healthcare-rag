import boto3
import pandas as pd
from io import StringIO

BUCKET_NAME = "healthcare-sandbox"
INPUT_PATH = "healthcare_dataset.csv"
OUTPUT_PATH = "healthcare_dataset_cleaned.csv"

s3 = boto3.client("s3")
obj = s3.get_object(Bucket=BUCKET_NAME, Key=INPUT_PATH)

df = pd.read_csv(obj["Body"])

print(f"Loaded {len(df)} rows")

df["Name"] = (df["Name"].astype(str).str.strip().str.title())
print(df.head())

csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_PATH, Body=csv_buffer.getvalue())

print(f"Cleaned dataset uploaded to s3://{BUCKET_NAME}/{OUTPUT_PATH}")