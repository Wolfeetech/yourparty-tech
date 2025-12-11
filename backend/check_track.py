from mongo_client import MongoDatabaseClient
import os

# Load .env manually if needed
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, _, value = line.partition('=')
                if key and value:
                     os.environ[key.strip()] = value.strip().strip('"').strip("'")

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri or "root:yourparty" in mongo_uri:
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
    pwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
    host = os.getenv("MONGO_HOST", "192.168.178.222")
    port = os.getenv("MONGO_PORT", "27017")
    if user and pwd:
        mongo_uri = f"mongodb://{user}:{pwd}@{host}:{port}/?authSource=admin"

print(f"Connecting with URI: {mongo_uri}")
db = MongoDatabaseClient(mongo_uri)
print("--- Dumping Ratings ---")
for r in db.ratings_collection.find():
    print(r)

