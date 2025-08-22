Project Overview

This project implements a semantic search and analysis system for patents and research papers. A user can enter a natural language query, and the system retrieves the most relevant documents. Along with search results, the platform provides sub-topic clustering and trend analysis to highlight emerging or declining areas of research.

The backend is built with FastAPI and uses Milvus as the vector database. The frontend is developed with Nuxt.js (Vue) and styled using Tailwind CSS.




Approach

Data Preparation
Patent abstracts came from g_patent_abstract.tsv, but this file did not include grant years. To support trend analysis, it was merged with a second dataset (2024.csv) containing publication years. The result was stored in merged_patent_data.tsv.
Research papers were collected using the OpenAlex API, including metadata such as title, abstract, publication year, and citation counts. If the API fetch failed, a synthetic dataset generator created realistic fallback data to ensure the system remained usable.

Vectorization and Indexing
Both patent and paper abstracts were converted into embeddings using the all-MiniLM-L6-v2 model from Sentence Transformers.
Metadata and embeddings were stored in Milvus for high-performance vector similarity search.

APIs
/search: Returns top-k relevant documents with optional filters (document type, year range, citation thresholds).
/analyze-subtopics: Clusters search results into sub-topics using KMeans and labels them with common keywords.
/trend-analysis: Aggregates results by year, calculates citation trends, and classifies clusters as growing, stable, or declining.




Frontend
index.vue: Main page with query input and search results.
SubtopicAnalysis.vue: Displays sub-topic clusters and keywords.
TrendAnalysis.vue: Shows time trends and velocity analysis for each cluster.




Assumptions, Challenges, and Trade-offs
Patents dataset: The original patents abstract file lacked year information, so it was merged with another dataset to enable trend analysis.

Clustering choice: KMeans was used for its speed and simplicity. More advanced clustering methods (like BERTopic or HDBSCAN) might yield better topic quality but would require more resources.

Visualization: The system includes basic trend and sub-topic visualization. More advanced, interactive heatmaps or charts could improve usability but were not prioritized here.

Deployment: The solution runs locally. Deployment to a live platform was not part of the scope.