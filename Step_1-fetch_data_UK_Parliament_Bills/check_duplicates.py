import sqlite3

# Connect to your bills.db
conn = sqlite3.connect('bills.db')
cursor = conn.cursor()

# Find billIds that appear more than once
cursor.execute("""
SELECT bill_id, COUNT(*) 
FROM bills 
GROUP BY bill_id 
HAVING COUNT(*) > 1;
""")
duplicates = cursor.fetchall()

print("Duplicate bill_ids and counts:")
for bill_id, count in duplicates:
    print(f"Bill ID: {bill_id}, Count: {count}")

# Now print details for these duplicates
print("\nDetails for duplicate bill_ids:")
for bill_id, _ in duplicates:
    cursor.execute("SELECT * FROM bills WHERE bill_id = ?;", (bill_id,))
    rows = cursor.fetchall()
    print(f"\nBill ID: {bill_id}")
    for row in rows:
        print(row)

conn.close()

