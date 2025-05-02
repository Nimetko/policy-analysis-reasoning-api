import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API_KEY")

supabase = create_client(url, key)

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

if all_rows:
    df_bills = pd.DataFrame(all_rows)
    print(f"✅ Total rows retrieved from '{table_name}': {len(df_bills)}")
    print(df_bills.head())
else:
    print(f"❌ No data retrieved from '{table_name}'. Check table name, RLS, or API key.")
