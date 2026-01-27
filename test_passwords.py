import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri_orig = "mongodb+srv://AmirAmirali:SepqZM9YulYjynk@storyforge.bpvfcqg.mongodb.net/?appName=StoryForge"
mongo_uri_v1 = "mongodb+srv://AmirAmirali:SepqZM9Yu1Yjynk@storyforge.bpvfcqg.mongodb.net/?appName=StoryForge"

uris = [("Original", mongo_uri_orig), ("With '1'", mongo_uri_v1)]

for name, uri in uris:
    print(f"Testing {name}...", flush=True)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"SUCCESS with {name}!", flush=True)
        exit(0)
    except Exception as e:
        print(f"FAILED with {name}: {e}", flush=True)

