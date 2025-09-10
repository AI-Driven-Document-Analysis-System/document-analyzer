import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path='chroma_db', settings=Settings(anonymized_telemetry=False))

# Delete the entire collection and recreate it
try:
    client.delete_collection('documents')
    print("Deleted old documents collection")
except:
    print("Collection didn't exist or already deleted")

# Create fresh collection
collection = client.create_collection('documents')
print(f"Created fresh documents collection. Total chunks: {collection.count()}")
