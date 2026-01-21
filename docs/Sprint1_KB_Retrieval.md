Sprint1_KB_Retrieval# Sprint 1 – Knowledge Base & Retrieval Tool Setup  
**Duration:** 2 weeks  
**Sprint Goal:** Stand up the foundational knowledge base and retrieval pipeline so that our specialist agents can query real policy/vendor docs.

### Work Items  
- Create GCS bucket: `gs://urbannexus-smart-city-kb` and folder layout:
  - `policies/nist-ai-rmf/`
  - `policies/sunshine-law/`
  - `policies/cjis/`
  - `smart-city-guides/`
  - `vendors/ubicquia/`
  - `local-gov/`
- Upload seed documents (NIST AI RMF 1.0, Florida Sunshine Law manuals, CJIS Policy v6.0, smart-city privacy/security guides, vendor spec PDFs)  
- Commit `smart-city/rag/corpus_seed.md` manifest listing all items (title, filename, source URL, GCS path)  
- Create Vertex AI Search data store(s) pointing to the GCS paths  
- Create Vertex AI Search App/Engine named `urbannexus-smart-city` and attach the data store(s)  
- Build retrieval tool: `smart-city/rag/vertex_search.py` with function `search_app(query: str, top_k: int = 8) -> list[Doc]`  
- Add “Makefile” or script target `kb.health` that runs a sample query (e.g., “Sunshine Law video retention”) and prints top 3 titles + URIs  
- Ensure permissions/IAM: enable `discoveryengine.googleapis.com`, grant access to GCS bucket and data store create rights  
- **Definition of Done:**  
  - `kb.health` returns valid titles + URIs  
  - Retrieval tool returns structured docs `{title, uri, snippet, source}`  
  - Seed corpus uploaded and manifest committed  

### Risks & Considerations  
- GCS object permissions must allow the Vertex Search service account to read objects  
- Data store naming/region must match for App creation  
- Retrieval tool output must be stable and parseable