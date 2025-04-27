import subprocess

# Step 1: Fetch bills from Parliament API
print("\n=== STEP 1: Fetching Bills ===")
subprocess.run(["python", "fetch_bills.py"], check=True)

# Step 2: Process downloaded bills (flatten and clean)
print("\n=== STEP 2: Processing Downloaded Data ===")
subprocess.run(["python", "process_downloaded_data.py"], check=True)

# Step 3: Create local SQLite database
print("\n=== STEP 3: Creating Local Bills Database ===")
subprocess.run(["python", "create_local_bills_database.py"], check=True)

# Step 4: (Optional) Check for duplicates
print("\n=== STEP 4: Checking for Duplicates ===")
subprocess.run(["python", "check_duplicates.py"], check=True)

# Step 5: Test the final bills database
print("\n=== STEP 5: Testing Bills Database ===")
subprocess.run(["python", "test_bills_db.py"], check=True)

print("\n✅ Pipeline completed successfully!")

