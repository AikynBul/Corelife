import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    print("ERROR: MONGO_URI not found in .env file.")
    exit(1)

import sys
# Mask password for printing
masked_uri = mongo_uri.replace("SepqZM9YulYjynk", "******")
print(f"Testing connection to: {masked_uri}")
print(f"URI Length: {len(mongo_uri)}")
print(f"URI Repr: {repr(mongo_uri)}")
print(f"URI Chars: {' '.join(hex(ord(c)) for c in mongo_uri)}")
sys.stdout.flush()




try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Trigger a connection
    client.admin.command('ping')
    print("SUCCESS: Connected to MongoDB!")
except Exception as e:
    import traceback
    print(f"ERROR: Failed to connect.")
    print(f"Exception Type: {type(e).__name__}")
    print(f"Exception Message: {str(e)}")
    traceback.print_exc()

