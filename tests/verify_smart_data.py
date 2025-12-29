import os
from pymongo import MongoClient
import logging

# Hardcoded for server check (skipping env issues)
mongo_uri = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/yourparty?authSource=admin"
print(f"Connecting to: {mongo_uri}")
client = MongoClient(mongo_uri)
db = client["yourparty"]
collection = db["tracks"]

# Find a track with a "Smart Genre" (not Unknown, not Music)
print("--- Searching for Smart Tagged Tracks ---")
sample = collection.find_one({"genre": {"$nin": ["Unknown", "Music", ""]}})

if sample:
    print(f"FOUND Track: {sample.get('title')}")
    print(f"ID: {sample.get('_id')}")
    print(f"Genre: {sample.get('genre')}  <-- VERIFY THIS IS SPECIFIC")
    print(f"Mood:  {sample.get('mood')}")
    print(f"Path:  {sample.get('relative_path')}")
else:
    print("NO SMART TAGS FOUND! Database might not be updated.")

# Check count of updated genres
count = collection.count_documents({"genre": {"$nin": ["Unknown", "Music", ""]}})
print(f"Total Smart Tagged Tracks: {count}")
