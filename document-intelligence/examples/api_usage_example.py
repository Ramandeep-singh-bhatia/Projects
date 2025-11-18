"""
Example script demonstrating API usage for Document Intelligence Platform.
"""

import requests
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"
SAMPLE_DOCUMENT = "sample.pdf"  # Replace with your document


def upload_document(file_path: str):
    """Upload a document to the platform."""
    print(f"\n📤 Uploading document: {file_path}")

    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f)}
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful! Document ID: {data['id']}")
        return data['id']
    else:
        print(f"❌ Upload failed: {response.json()}")
        return None


def check_document_status(doc_id: int):
    """Check document processing status."""
    print(f"\n🔍 Checking status of document {doc_id}")

    response = requests.get(f"{API_BASE_URL}/documents/{doc_id}")

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Type: {data['document_type']}")
        if data.get('word_count'):
            print(f"Words: {data['word_count']}")
        return data
    else:
        print(f"❌ Failed to get status: {response.json()}")
        return None


def search_documents(query: str, strategy: str = "hybrid", top_k: int = 5):
    """Search for documents."""
    print(f"\n🔍 Searching for: '{query}'")
    print(f"Strategy: {strategy}")

    payload = {
        "query": query,
        "top_k": top_k,
        "strategy": strategy
    }

    response = requests.post(f"{API_BASE_URL}/search/", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {data['total_results']} results")
        print(f"Execution time: {data['execution_time'] * 1000:.0f}ms")

        for i, result in enumerate(data['results'][:3], 1):
            print(f"\n--- Result {i} ---")
            print(f"Score: {result['score']:.4f}")
            print(f"Content: {result['content'][:200]}...")

        return data
    else:
        print(f"❌ Search failed: {response.json()}")
        return None


def ask_question(question: str, strategy: str = "hybrid", top_k: int = 3):
    """Ask a question using RAG."""
    print(f"\n💬 Asking: '{question}'")
    print(f"Strategy: {strategy}")

    payload = {
        "question": question,
        "top_k": top_k,
        "strategy": strategy
    }

    response = requests.post(f"{API_BASE_URL}/search/query", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Answer generated!")
        print(f"Confidence: {data['confidence'] * 100:.1f}%")
        print(f"Sources used: {data['num_sources']}")
        print(f"Execution time: {data['execution_time']:.2f}s")

        print(f"\n📝 Answer:")
        print(data['answer'])

        print(f"\n📚 Sources:")
        for source in data['sources']:
            print(f"\n  Source {source['number']} (Score: {source['score']:.4f})")
            print(f"  {source['content'][:150]}...")

        return data
    else:
        print(f"❌ Query failed: {response.json()}")
        return None


def get_analytics():
    """Get platform analytics."""
    print("\n📊 Fetching analytics...")

    # Document overview
    response = requests.get(f"{API_BASE_URL}/analytics/overview")
    if response.status_code == 200:
        data = response.json()
        print("\n📄 Document Overview:")
        print(f"  Total documents: {data['total_documents']}")
        print(f"  Total pages: {data['total_pages']}")
        print(f"  Total words: {data['total_words']:,}")

        if data['documents_by_type']:
            print("\n  Documents by type:")
            for doc_type, count in data['documents_by_type'].items():
                print(f"    {doc_type}: {count}")

    # Search stats
    response = requests.get(f"{API_BASE_URL}/analytics/search-stats?days=30")
    if response.status_code == 200:
        data = response.json()
        print("\n🔍 Search Statistics (Last 30 days):")
        print(f"  Total searches: {data['total_searches']}")
        print(f"  Avg. execution time: {data['avg_execution_time']:.0f}ms")

        if data['top_queries']:
            print("\n  Top queries:")
            for q in data['top_queries'][:5]:
                print(f"    '{q['query']}' ({q['count']} times)")


def main():
    """Main demonstration function."""
    print("=" * 60)
    print("Document Intelligence Platform - API Usage Example")
    print("=" * 60)

    # 1. Upload a document (commented out - provide your own file)
    # doc_id = upload_document("path/to/your/document.pdf")
    # if doc_id:
    #     time.sleep(2)  # Wait for processing
    #     check_document_status(doc_id)

    # 2. Search examples
    print("\n" + "=" * 60)
    print("SEARCH EXAMPLES")
    print("=" * 60)

    # Hybrid search
    search_documents(
        query="machine learning algorithms",
        strategy="hybrid",
        top_k=5
    )

    time.sleep(1)

    # Vector search
    search_documents(
        query="data analysis techniques",
        strategy="vector",
        top_k=5
    )

    time.sleep(1)

    # Multi-query search
    search_documents(
        query="neural networks",
        strategy="multi_query",
        top_k=5
    )

    # 3. RAG Question Answering
    print("\n" + "=" * 60)
    print("RAG QUESTION ANSWERING")
    print("=" * 60)

    ask_question(
        question="What are the main topics discussed in the documents?",
        strategy="hybrid",
        top_k=5
    )

    time.sleep(1)

    ask_question(
        question="Summarize the key findings from the research papers",
        strategy="multi_query",
        top_k=5
    )

    # 4. Get analytics
    print("\n" + "=" * 60)
    print("ANALYTICS")
    print("=" * 60)

    get_analytics()

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
