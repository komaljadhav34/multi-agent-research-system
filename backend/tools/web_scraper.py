import re
import logging
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
try:
    import chromadb
    from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    # Satisfy base inheritance constraints if ChromaDB is not installed
    class EmbeddingFunction:
        pass
    Documents = List[str]
    Embeddings = List[List[float]]

logger = logging.getLogger(__name__)

class SimpleEmbeddingFunction(EmbeddingFunction):
    """
    A deterministic, zero-dependency, lightning-fast embedding function.
    Creates 128-dimensional vectors using word-hash frequencies.
    Allows ChromaDB to run instantly without downloading heavy model files (PyTorch/Transformers).
    """
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            # Clean and normalize text
            text = re.sub(r'[^a-zA-Z0-9\s]', '', doc.lower())
            words = text.split()
            
            vector = [0.0] * 128
            # Compute term frequencies into 128 buckets
            for word in words:
                idx = hash(word) % 128
                vector[idx] += 1.0
                
            # L2 Normalize the vector to ensure proper cosine similarity matching
            magnitude = sum(x * x for x in vector) ** 0.5
            if magnitude > 0:
                vector = [x / magnitude for x in vector]
            
            embeddings.append(vector)
        return embeddings

def scrape_url(url: str) -> str:
    """Scrapes raw text from a URL and cleans it up."""
    if not url:
        return ""
    try:
        logger.info(f"Scraping URL: {url}")
        # Use a realistic User-Agent to avoid getting blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # Timeout after 5 seconds to avoid hanging the researcher
        with httpx.Client(headers=headers, follow_redirects=True, timeout=5.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove boilerplate tags
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                
                # Extract text
                text = soup.get_text(separator=" ")
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                return text
            else:
                logger.warning(f"Failed to scrape {url}: Status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
    return ""

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Splits text into chunks with overlapping windows."""
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks

def store_and_query_vectors(subtopic: str, scraped_sources: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Chunks scraped contents, indexes them in a local in-memory ChromaDB collection,
    queries the vector database for the given subtopic, and returns the top matches.
    """
    if not scraped_sources:
        return []
        
    # Check if ChromaDB is installed in active environment
    if not CHROMA_AVAILABLE:
        logger.info("ChromaDB package is not installed. Using raw source content fallback.")
        print("[INFO] ChromaDB package is not installed. Using raw source content fallback.")
        return [
            {
                "snippet": src.get("content", ""),
                "title": src.get("title", "Source"),
                "url": src.get("url", ""),
                "relevance_score": 0.8
            }
            for src in scraped_sources[:top_k]
        ]

    try:
        # Initialize an ephemeral (in-memory) ChromaDB client
        chroma_client = chromadb.EphemeralClient()
        # Create a unique collection for this subtopic
        collection_name = f"subtopic_{abs(hash(subtopic))}"
        
        # Use our lightweight custom embedding function
        emb_fn = SimpleEmbeddingFunction()
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=emb_fn
        )
        
        documents = []
        metadatas = []
        ids = []
        
        doc_count = 0
        for src in scraped_sources:
            title = src.get("title", "Source")
            url = src.get("url", "")
            raw_text = src.get("raw_content") or src.get("content", "")
            
            # Scrape full text if raw_content is short and URL is available
            # Note: We prioritize raw_content from Tavily advanced search, but scrape if empty
            if len(raw_text) < 200 and url:
                scraped_text = scrape_url(url)
                if scraped_text:
                    raw_text = scraped_text
            
            # Chunk the source content
            chunks = chunk_text(raw_text)
            for idx, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "title": title,
                    "url": url,
                    "chunk_id": idx
                })
                ids.append(f"doc_{doc_count}_chunk_{idx}")
            doc_count += 1
            
        if not documents:
            return []
            
        # Add to ChromaDB vector collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Query ChromaDB collection
        results = collection.query(
            query_texts=[subtopic],
            n_results=min(top_k, len(documents))
        )
        
        # Format the top matching documents
        formatted_matches = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metadata_list = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            
            for d, m, dist in zip(docs, metadata_list, distances):
                formatted_matches.append({
                    "snippet": d,
                    "title": m["title"],
                    "url": m["url"],
                    "relevance_score": round(1.0 - dist, 3) # Simple distance-to-similarity conversion
                })
                
        return formatted_matches
    except Exception as e:
        logger.error(f"Error indexing or querying vector store: {e}")
        # Return fallback items from the scraped sources directly if vector indexing fails
        return [
            {
                "snippet": src.get("content", ""),
                "title": src.get("title", "Source"),
                "url": src.get("url", ""),
                "relevance_score": 0.8
            }
            for src in scraped_sources[:top_k]
        ]
