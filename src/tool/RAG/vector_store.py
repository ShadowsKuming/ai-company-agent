"""
Vector Store for RAG system - stores and retrieves financial knowledge
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[WARN] sentence-transformers not available. Install with: pip install sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[WARN] faiss not available. Install with: pip install faiss-cpu")


class FinancialKnowledgeStore:
    """Vector store for financial analysis knowledge"""
    
    def __init__(self, store_path: str = "src/tool/RAG/knowledge_store"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        self.encoder = None
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Initialize components if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            print("[OK] Sentence transformer loaded")
        else:
            print("[WARN] Using basic text matching instead of vector search")
        
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load existing knowledge base"""
        docs_file = self.store_path / "documents.json"
        index_file = self.store_path / "faiss_index.bin"
        
        try:
            if docs_file.exists():
                with open(docs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
                
                print(f"[OK] Loaded {len(self.documents)} documents from knowledge base")
            
            if FAISS_AVAILABLE and index_file.exists() and self.encoder:
                self.index = faiss.read_index(str(index_file))
                print("[OK] FAISS index loaded")
                
        except Exception as e:
            print(f"[WARN] Could not load existing knowledge base: {e}")
            self._create_default_knowledge()
    
    def _create_default_knowledge(self):
        """Create default financial knowledge base"""
        default_knowledge = [
            {
                "content": "Financial ratio analysis: Current ratio measures liquidity (current assets / current liabilities). Above 1.5 is generally good.",
                "category": "financial_ratios",
                "importance": 0.8
            },
            {
                "content": "R&D spending analysis: Companies spending >15% of revenue on R&D are typically innovation-focused. Tech companies average 10-20%.",
                "category": "rd_analysis", 
                "importance": 0.9
            },
            {
                "content": "CEO leadership assessment: Look for track record, tenure, strategic vision, and ability to execute. Previous company performance is key indicator.",
                "category": "leadership",
                "importance": 0.7
            },
            {
                "content": "Technology competitive advantage: Patent portfolio strength, R&D efficiency, and market adoption rate of innovations are key metrics.",
                "category": "technology",
                "importance": 0.8
            },
            {
                "content": "Sentiment analysis interpretation: Social media sentiment should be weighted less than news sentiment. Look for sentiment trend changes over time.",
                "category": "sentiment",
                "importance": 0.6
            },
            {
                "content": "Investment recommendation framework: Consider growth potential, financial stability, leadership quality, competitive position, and market sentiment.",
                "category": "investment",
                "importance": 1.0
            }
        ]
        
        for item in default_knowledge:
            self.add_document(
                content=item["content"],
                metadata={
                    "category": item["category"],
                    "importance": item["importance"],
                    "source": "default_knowledge",
                    "created": datetime.now().isoformat()
                }
            )
        
        print(f"[OK] Created default knowledge base with {len(default_knowledge)} documents")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None):
        """Add document to knowledge store"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "added_at": datetime.now().isoformat(),
            "doc_id": len(self.documents)
        })
        
        self.documents.append(content)
        self.metadata.append(metadata)
        
        # Update vector index if available
        if self.encoder and FAISS_AVAILABLE:
            self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild FAISS index with current documents"""
        if not self.documents or not self.encoder:
            return
        
        try:
            # Encode all documents
            embeddings = self.encoder.encode(self.documents)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(embeddings.astype('float32'))
                print(f"[OK] FAISS index rebuilt with {len(self.documents)} documents")
            
        except Exception as e:
            print(f"[WARN] Could not rebuild index: {e}")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.documents:
            return []
        
        # Vector search if available
        if self.encoder and self.index and FAISS_AVAILABLE:
            return self._vector_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        try:
            # Encode query
            query_embedding = self.encoder.encode([query])
            
            # Search
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "similarity": float(1 / (1 + distance)),  # Convert distance to similarity
                        "rank": i + 1
                    })
            
            return results
            
        except Exception as e:
            print(f"[WARN] Vector search failed: {e}")
            return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        query_words = set(query.lower().split())
        
        results = []
        for i, doc in enumerate(self.documents):
            doc_words = set(doc.lower().split())
            overlap = len(query_words.intersection(doc_words))
            
            if overlap > 0:
                similarity = overlap / len(query_words.union(doc_words))
                results.append({
                    "content": doc,
                    "metadata": self.metadata[i],
                    "similarity": similarity,
                    "rank": 0
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        for i, result in enumerate(results[:top_k]):
            result["rank"] = i + 1
        
        return results[:top_k]
    
    def get_context_for_analysis(self, analysis_type: str, company_data: Dict[str, Any] = None) -> str:
        """Get relevant context for specific analysis type"""
        # Construct search query based on analysis type and company data
        queries = {
            "cash_flow": f"cash flow analysis revenue R&D spending {company_data.get('sector', '') if company_data else ''}",
            "profit": f"profit margins profitability financial ratios {company_data.get('industry', '') if company_data else ''}",
            "ceo": f"CEO leadership analysis executive assessment {company_data.get('ceo_name', '') if company_data else ''}",
            "technology": f"technology analysis patents competitive advantage innovation {company_data.get('sector', '') if company_data else ''}",
            "sentiment": f"sentiment analysis market perception social media news {company_data.get('ticker', '') if company_data else ''}",
            "investment": f"investment recommendation framework analysis methodology {company_data.get('sector', '') if company_data else ''}"
        }
        
        query = queries.get(analysis_type, f"{analysis_type} analysis")
        results = self.search(query, top_k=2)
        
        if not results:
            return ""
        
        # Combine relevant context
        context_parts = []
        for result in results:
            context_parts.append(f"[Knowledge] {result['content']}")
        
        return "\n".join(context_parts)
    
    def save(self):
        """Save knowledge store to disk"""
        try:
            # Save documents and metadata
            docs_file = self.store_path / "documents.json"
            data = {
                "documents": self.documents,
                "metadata": self.metadata,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(docs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save FAISS index
            if self.index and FAISS_AVAILABLE:
                index_file = self.store_path / "faiss_index.bin"
                faiss.write_index(self.index, str(index_file))
            
            print(f"[OK] Knowledge store saved with {len(self.documents)} documents")
            
        except Exception as e:
            print(f"[WARN] Could not save knowledge store: {e}")


# Global instance
knowledge_store = FinancialKnowledgeStore()