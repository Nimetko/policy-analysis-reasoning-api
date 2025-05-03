import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from openai import OpenAI
import json
import time

# Load environment variables
load_dotenv()

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API_KEY")
supabase = create_client(url, key)

# Set up OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=openai_api_key)

# Retrieve all rows from Supabase (filtered from 2020 onwards)
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

df_bills = pd.DataFrame(all_rows)
print(f"✅ Loaded {len(df_bills)} bills")

# Filter to bills from 2020 onwards
if 'lastUpdate' in df_bills.columns:
    df_bills['lastUpdate'] = pd.to_datetime(df_bills['lastUpdate'], errors='coerce')
    df_bills = df_bills[df_bills['lastUpdate'] >= '2020-01-01'].copy()
    print(f"📅 Filtered to {len(df_bills)} bills from 2020 onwards")
else:
    print("⚠️ 'lastUpdate' column missing from dataset")

# Categorize shortTitles into policyArea using batch GPT calls
if 'shortTitle' in df_bills.columns:
    unique_titles = df_bills.dropna(subset=['shortTitle']).drop_duplicates(subset=['shortTitle'])[['billId', 'shortTitle']]
    policy_map = {}
    batch_size = 50

    for i in range(0, len(unique_titles), batch_size):
    #     if i >= batch_size * 3:  # Limit to first 3 batches for testing
    #         break

        batch = unique_titles.iloc[i:i + batch_size]
        title_dict = {str(bid): title for bid, title in zip(batch['billId'], batch['shortTitle'])}

        prompt = f"""
Given the following UK bill short titles, classify each into one of the following policy areas:
Health, Education, Defense, Economy, Environment, Justice, Transport, Housing, Social Care, Other.

Return the result as a JSON object with the billId as key and policy area as value.

❗Important: Use the exact billId provided for keys.

Bills:
{json.dumps(title_dict, indent=2)}
"""
        try:
            completion = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            content = completion.choices[0].message.content.strip()

            # Sanitize GPT output
            if content.startswith("```"):
                content = content.strip("`").strip()
                if content.startswith("json"):
                    content = content[4:].strip()

            # Attempt to parse JSON
            result = json.loads(content)
            policy_map.update(result)
            print(f"✅ Processed batch {i // batch_size + 1}/{(len(unique_titles) + batch_size - 1) // batch_size}")
            for bill_id, area in result.items():
                title = title_dict.get(bill_id, "<Unknown>")
                print(f"🔹 {title} ({bill_id}) -> {area}")
            time.sleep(1.5)

        except json.JSONDecodeError:
            print(f"❌ JSON parsing error in batch {i // batch_size + 1}. Content was:\n{content}")
        except Exception as e:
            print(f"❌ Error in batch {i // batch_size + 1}: {e}")
            continue

    # Create mapping from shortTitle -> policyArea
    bid_to_title = unique_titles.set_index('billId')['shortTitle'].to_dict()
    short_title_to_policy = {bid_to_title[int(bid)]: area for bid, area in policy_map.items() if int(bid) in bid_to_title}

    # Apply mapping to all rows using shortTitle
    df_bills['policyArea'] = df_bills['shortTitle'].map(short_title_to_policy)
    print("✅ Added 'policyArea' to full dataset")

    # Save full updated dataset
    df_bills.to_csv("bills_with_policy_area_full.csv", index=False)
    print("💾 Saved full dataset with 'policyArea' to 'bills_with_policy_area_full.csv")
else:
    print("⚠️ 'shortTitle' column missing from dataset")
