import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API_KEY")
supabase = create_client(url, key)

# Load the enriched CSV file with policyArea
csv_path = "bills_with_policy_area_full.csv"
df = pd.read_csv(csv_path)

if 'billId' not in df.columns or 'policyArea' not in df.columns:
    print("❌ Missing 'billId' or 'policyArea' columns in CSV.")
    exit(1)

print(f"🔄 Preparing to update {len(df)} records with policyArea")

batch_size = 500
table_name = "all_bills_uk"

for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i + batch_size][['billId', 'policyArea']].dropna(subset=['policyArea'])
    records = batch.to_dict(orient="records")

    if not records:
        print(f"⚠️ Skipping empty batch {i//batch_size + 1}")
        continue

    try:
        supabase.table(table_name).upsert(records, on_conflict="billId").execute()
        print(f"✅ Updated batch {i//batch_size + 1} ({len(records)} records)")
    except Exception as e:
        print(f"❌ Failed batch {i//batch_size + 1}: {e}")
