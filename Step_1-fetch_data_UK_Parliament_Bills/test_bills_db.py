import sqlite3

conn = sqlite3.connect('bills.db')
cursor = conn.cursor()

# Count rows
cursor.execute("SELECT COUNT(*) FROM bills;")
print("Total bills:", cursor.fetchone()[0])

# Preview 5 bills
cursor.execute("SELECT bill_id, short_title, current_house FROM bills LIMIT 5;")
for row in cursor.fetchall():
    print(row)

# Bills that became laws
cursor.execute("SELECT bill_id, short_title FROM bills WHERE is_act = 1;")
acts = cursor.fetchall()
print("Bills that became Acts:")
for act in acts:
    print(act)

conn.close()

