import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path='chroma_db', settings=Settings(anonymized_telemetry=False))
collection = client.get_collection('documents')
print(f'Total chunks: {collection.count()}')

# Check for Gaussian Topology document chunks
gaussian_results = collection.get(
    where={"filename": "Gaussian Topology.pdf"},
    include=['metadatas']
)
print(f'Gaussian Topology chunks: {len(gaussian_results["ids"])}')

# Check for the specific document ID from logs: 307a30f0-288d-4587-9f9a-a281051ff932
new_doc_results = collection.get(
    where={"document_id": "307a30f0-288d-4587-9f9a-a281051ff932"},
    include=['metadatas']
)
print(f'New document (307a30f0) chunks: {len(new_doc_results["ids"])}')

# Show unique document IDs in database
all_results = collection.get(include=['metadatas'])
unique_docs = {}
for metadata in all_results['metadatas']:
    doc_id = metadata.get('document_id', 'MISSING')
    filename = metadata.get('filename', 'MISSING')
    if doc_id not in unique_docs:
        unique_docs[doc_id] = filename

print(f'\nUnique documents in database:')
for doc_id, filename in unique_docs.items():
    count = sum(1 for m in all_results['metadatas'] if m.get('document_id') == doc_id)
    print(f'  {doc_id}: {filename} ({count} chunks)')
