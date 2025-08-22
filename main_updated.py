from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
from pymilvus import utility
import json
from fastapi.middleware.cors import CORSMiddleware

#CONFIG 
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "mixed_documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# FASTAPI INIT 
app = FastAPI(title="Patent & Paper Search API with Trend Analysis")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain instead of "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
#  MILVUS INIT 
connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

# Updated schema for mixed documents
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=5000),
    FieldSchema(name="publication_year", dtype=DataType.INT32),
    FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=20),
    FieldSchema(name="citation_count", dtype=DataType.INT32),  # For papers, 0 for patents
]
schema = CollectionSchema(fields, description="Mixed patents and papers")

# Initialize collection variable
collection = None

#  EMBEDDINGS 
model = SentenceTransformer(EMBEDDING_MODEL)


def check_collection_exists():
    """Check if collection exists and has data"""
    global collection
    if COLLECTION_NAME in utility.list_collections():
        collection = Collection(name=COLLECTION_NAME)
        try:
            collection.load()
            count = collection.query(expr="", limit=1, output_fields=["document_id"])
            return len(count) > 0
        except:
            return False
    return False

def load_and_insert_mixed_data(patent_sample: int = 5000, paper_sample: int = 5000, force_reload: bool = False):
    """Load both patents and research papers."""
    global collection
    

    if not force_reload and check_collection_exists():
        print(f"Collection '{COLLECTION_NAME}' already exists with data. Skipping data loading.")
        print(f" Use force_reload=True if you want to reload data.")
        return
    # Drop and recreate collection
    if COLLECTION_NAME in utility.list_collections():
        utility.drop_collection(COLLECTION_NAME)
        print(" Dropped existing collection")
    
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    print(" Created new mixed documents collection")
    
    all_documents = []
    
    # Load patents
    try:
        print(f" Loading patents from merged_patent_data.tsv (first {patent_sample})...")
        patents = pd.read_csv("merged_patent_data.tsv", sep="\t", nrows=patent_sample).dropna()
        
        for _, row in patents.iterrows():
            all_documents.append({
                "document_id": str(row["patent_id"]),
                "title": f"Patent {row['patent_id']}",
                "abstract": str(row["patent_abstract"])[:4900],
                "publication_year": int(row["grant_year"]),
                "doc_type": "patent",
                "citation_count": 0  # Patents don't have citation counts in our data
            })
        print(f" Loaded {len(patents)} patents")
        
    except FileNotFoundError:
        print(" merged_patent_data.tsv not found, skipping patents")
    
    # Load research papers
    try:
        print(f" Loading papers from research_papers.csv (first {paper_sample})...")
        papers = pd.read_csv("research_papers.csv", nrows=paper_sample).dropna()
        
        for _, row in papers.iterrows():
            all_documents.append({
                "document_id": str(row["paper_id"]),
                "title": str(row["title"])[:900],  # Truncate long titles
                "abstract": str(row["abstract"])[:4900],
                "publication_year": int(row["publication_year"]),
                "doc_type": "paper",
                "citation_count": int(row.get("citation_count", 0))
            })
        print(f" Loaded {len(papers)} papers")
        
    except FileNotFoundError:
        print(" research_papers.csv not found, skipping papers")
    
    if not all_documents:
        print(" No documents loaded!")
        return
    
    print(f" Generating embeddings for {len(all_documents)} documents...")
    abstracts = [doc["abstract"] for doc in all_documents]
    embeddings = model.encode(abstracts, show_progress_bar=True)
    embeddings = np.asarray(embeddings, dtype=np.float32)
    
    # Prepare data for insertion
    vectors = embeddings.tolist()
    document_ids = [doc["document_id"] for doc in all_documents]
    titles = [doc["title"] for doc in all_documents]
    abstracts = [doc["abstract"] for doc in all_documents]
    years = [doc["publication_year"] for doc in all_documents]
    doc_types = [doc["doc_type"] for doc in all_documents]
    citations = [doc["citation_count"] for doc in all_documents]
    
    print("💾 Inserting into Milvus...")
    collection.insert(
        data=[vectors, document_ids, titles, abstracts, years, doc_types, citations],
        fields=["vector", "document_id", "title", "abstract", "publication_year", "doc_type", "citation_count"]
    )
    
    print("⚡ Creating index...")
    collection.create_index(
        "vector",
        {"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 128}}
    )
    collection.load()
    
    print(f" Successfully indexed {len(all_documents)} documents")
    print(f" Patents: {sum(1 for d in all_documents if d['doc_type'] == 'patent')}")
    print(f" Papers: {sum(1 for d in all_documents if d['doc_type'] == 'paper')}")

# Load data on startup
load_and_insert_mixed_data()

#API MODELS 
class SearchRequest(BaseModel):
    query: str
    top_k: int = 50
    doc_type: str = "both"  # patents, papers, both
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    min_citations: Optional[int] = None  # For papers

class SubTopicAnalysisRequest(BaseModel):
    search_results: List[Dict]
    n_clusters: int = 5

#  API ENDPOINTS 

@app.post("/search")
def search_documents(req: SearchRequest):
    """Enhanced search with comprehensive filtering."""
    
    query_vec = model.encode([req.query])[0].tolist()
    
    # Build complex filter
    filters = []
    
    if req.doc_type != "both":
        filters.append(f'doc_type == "{req.doc_type}"')
    
    if req.year_start:
        filters.append(f"publication_year >= {req.year_start}")
    if req.year_end:
        filters.append(f"publication_year <= {req.year_end}")
        
    if req.min_citations and req.doc_type in ["papers", "both"]:
        filters.append(f"citation_count >= {req.min_citations}")
    
    filter_expr = " and ".join(filters) if filters else None
    
    results = collection.search(
        data=[query_vec],
        anns_field="vector",
        param={"metric_type": "IP", "params": {"nprobe": 10}},
        limit=req.top_k,
        expr=filter_expr,
        output_fields=["document_id", "title", "abstract", "publication_year", "doc_type", "citation_count"]
    )
    
    search_results = []
    for hit in results[0]:
        result = {
            "document_id": hit.entity.get("document_id"),
            "title": hit.entity.get("title"),
            "abstract": hit.entity.get("abstract"),
            "publication_year": hit.entity.get("publication_year"),
            "doc_type": hit.entity.get("doc_type"),
            "citation_count": hit.entity.get("citation_count"),
            "relevance_score": hit.distance
        }
        search_results.append(result)
    
    return {
        "results": search_results,
        "total_found": len(search_results),
        "query": req.query,
        "filters_applied": {
            "doc_type": req.doc_type,
            "year_range": f"{req.year_start or 'all'} - {req.year_end or 'all'}",
            "min_citations": req.min_citations
        }
    }

@app.post("/analyze-subtopics")
def analyze_subtopics(req: SubTopicAnalysisRequest):
    """Advanced clustering with better topic naming."""
    
    if len(req.search_results) < req.n_clusters:
        return {"error": f"Need at least {req.n_clusters} results for clustering"}
    
    abstracts = [result["abstract"] for result in req.search_results]
    embeddings = model.encode(abstracts)
    
    # Clustering
    kmeans = KMeans(n_clusters=req.n_clusters, random_state=42, n_init="auto")
    cluster_labels = kmeans.fit_predict(embeddings)
    
    # Group by cluster
    clusters = defaultdict(list)
    for i, label in enumerate(cluster_labels):
        req.search_results[i]["cluster_id"] = int(label)
        clusters[int(label)].append(req.search_results[i])
    
    # Enhanced topic naming
    cluster_summaries = {}
    for cluster_id, documents in clusters.items():
        # Extract meaningful terms from titles and abstracts
        titles_text = " ".join([doc["title"] for doc in documents])
        abstracts_text = " ".join([doc["abstract"][:200] for doc in documents])
        all_text = (titles_text + " " + abstracts_text).lower()
        
        # Filter for technical terms (length > 3, contains letters)
        words = [w for w in all_text.split() if len(w) > 3 and w.isalnum()]
        
        # Get most common technical terms
        common_terms = [word for word, count in Counter(words).most_common(10) 
                       if count > 1 and len(word) > 4][:4]
        
        # Calculate cluster stats
        doc_types = [doc["doc_type"] for doc in documents]
        years = [doc["publication_year"] for doc in documents]
        citations = [doc["citation_count"] for doc in documents if doc["citation_count"] > 0]
        
        cluster_summaries[cluster_id] = {
            "name": f"Cluster {cluster_id + 1}: {', '.join(common_terms[:3])}",
            "keywords": common_terms,
            "documents": documents,
            "stats": {
                "size": len(documents),
                "patents": doc_types.count("patent"),
                "papers": doc_types.count("paper"),
                "year_range": f"{min(years)} - {max(years)}",
                "avg_citations": round(sum(citations) / len(citations), 1) if citations else 0
            }
        }
    
    return {"clusters": cluster_summaries}

@app.post("/trend-analysis")
def analyze_trends(req: SearchRequest):
    """Comprehensive trend analysis with velocity calculations."""
    
    # Get search results
    search_response = search_documents(req)
    results = search_response["results"]
    
    if len(results) < 10:
        return {"error": "Need at least 10 results for meaningful trend analysis"}
    
    # Cluster the results
    cluster_req = SubTopicAnalysisRequest(search_results=results, n_clusters=min(5, len(results)//3))
    cluster_response = analyze_subtopics(cluster_req)
    
    if "error" in cluster_response:
        return cluster_response
    
    # Calculate trends
    trend_data = {}
    
    for cluster_id, cluster_info in cluster_response["clusters"].items():
        documents = cluster_info["documents"]
        
        # Year-wise analysis
        yearly_counts = defaultdict(lambda: {"patents": 0, "papers": 0, "total": 0})
        total_citations = defaultdict(int)
        
        for doc in documents:
            year = doc["publication_year"]
            yearly_counts[year]["total"] += 1
            yearly_counts[year][f"{doc['doc_type']}s"] += 1
            
            if doc["citation_count"] > 0:
                total_citations[year] += doc["citation_count"]
        
        years = sorted(yearly_counts.keys())
        
        # Velocity calculation (comparing recent vs older periods)
        if len(years) >= 4:
            recent_years = years[-2:]  # Last 2 years
            older_years = years[:-2]   # All previous years
            
            recent_count = sum(yearly_counts[year]["total"] for year in recent_years)
            older_count = sum(yearly_counts[year]["total"] for year in older_years)
            
            # Average per year
            recent_avg = recent_count / len(recent_years)
            older_avg = older_count / len(older_years) if older_years else 1
            
            velocity = recent_avg - older_avg
            velocity_pct = (velocity / older_avg) * 100 if older_avg > 0 else 0
            
            trend_status = "growing" if velocity > 0.5 else "declining" if velocity < -0.5 else "stable"
        else:
            velocity = 0
            velocity_pct = 0
            trend_status = "insufficient_data"
        
        trend_data[cluster_id] = {
            "cluster_name": cluster_info["name"],
            "keywords": cluster_info["keywords"],
            "yearly_data": dict(yearly_counts),
            "citations_by_year": dict(total_citations),
            "trend_metrics": {
                "velocity": round(velocity, 2),
                "velocity_percentage": round(velocity_pct, 1),
                "trend_status": trend_status,
                "total_documents": len(documents),
                "year_span": f"{min(years)} - {max(years)}"
            },
            "composition": cluster_info["stats"]
        }
    
    return {
        "query": req.query,
        "trend_analysis": trend_data,
        "summary": {
            "total_documents": len(results),
            "patents": len([r for r in results if r["doc_type"] == "patent"]),
            "papers": len([r for r in results if r["doc_type"] == "paper"]),
            "year_range": f"{min(r['publication_year'] for r in results)} - {max(r['publication_year'] for r in results)}",
            "clusters_analyzed": len(trend_data)
        }
    }

@app.get("/health")
def health_check():
    """System health check."""
    try:
        collection.query(expr="", limit=1, output_fields=["doc_type"])
        return {"status": "healthy", "collection": COLLECTION_NAME}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/")
def root():
    return {
        "message": "Patent & Research Paper Search API",
        "version": "2.0",
        "endpoints": {
            "/search": "Search patents and papers",
            "/analyze-subtopics": "Cluster search results into topics",
            "/trend-analysis": "Analyze publication trends and velocity",
            "/health": "System health check"
        },
        "features": [
            "Mixed patent and paper search",
            "Advanced filtering (year, type, citations)",
            "Intelligent sub-topic clustering",
            "Trend velocity analysis",
            "Publication pattern insights"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)