import os
import sys
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv


def upload_csv_to_supabase(csv_file_path, table_name):
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_API_KEY")

    supabase = create_client(url, key)

    # Read your CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert DataFrame to list of dicts
    data = df.to_dict(orient='records')

    # Insert data into Supabase
    for row in data:
        response = supabase.table(table_name).insert(row).execute()
        if response.error:
            print(f"Error inserting row {row}: {response.error}")
        else:
            print(f"Inserted row: {row}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python upload_to_supabase.py <csv_file_path> <table_name>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    table_name = sys.argv[2]

    upload_csv_to_supabase(csv_file_path, table_name)
