import sqlite3
import pandas as pd

# Load the CSV into a pandas DataFrame
df = pd.read_csv("flat_bills.csv")

# Connect to SQLite database (creates 'bills.db' if it doesn't exist)
conn = sqlite3.connect('bills.db')
cursor = conn.cursor()

# Create the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY,
        short_title TEXT,
        current_house TEXT,
        originating_house TEXT,
        last_update TEXT,
        bill_withdrawn BOOLEAN,
        is_defeated BOOLEAN,
        is_act BOOLEAN,
        current_stage_description TEXT,
        current_stage_house TEXT,
        current_stage_abbreviation TEXT
    )
''')

# Insert the data from DataFrame into the database
df.rename(columns={
    'billId': 'bill_id',
    'shortTitle': 'short_title',
    'currentHouse': 'current_house',
    'originatingHouse': 'originating_house',
    'lastUpdate': 'last_update',
    'billWithdrawn': 'bill_withdrawn',
    'isDefeated': 'is_defeated',
    'isAct': 'is_act',
    'currentStage_description': 'current_stage_description',
    'currentStage_house': 'current_stage_house',
    'currentStage_abbreviation': 'current_stage_abbreviation'
}, inplace=True)

df.to_sql('bills', conn, if_exists='replace', index=False)

# Done!
print("✅ Data successfully loaded into bills.db")

# Optional: test basic queries
print("\nSample bills:")
for row in cursor.execute("SELECT bill_id, short_title, current_house, is_act FROM bills LIMIT 5"):
    print(row)

# Close connection
conn.commit()
conn.close()

