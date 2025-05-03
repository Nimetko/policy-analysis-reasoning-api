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

# Download all rows with policyArea
print("🔄 Downloading records from Supabase...")
table_name = "all_bills_uk"
batch_size = 1000
offset = 0
all_rows = []

while True:
    response = supabase.table(table_name).select("*").range(offset, offset + batch_size - 1).execute()
    if not response.data:
        break
    all_rows.extend(response.data)
    offset += batch_size

# Convert to DataFrame
df = pd.DataFrame(all_rows)

if "policyArea" not in df.columns:
    print("❌ 'policyArea' column missing from Supabase table.")
else:
    output_file = "bills_with_policy_area_full.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Downloaded {len(df)} records to '{output_file}'")

