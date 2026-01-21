"""
UrbanNexus Smart-City Use Case: RAG Configuration

This module contains the configuration for the Retrieval-Augmented Generation
(RAG) pipeline, which uses Google Cloud's Vertex AI Search and
Vertex AI Vector Search.

NOTE: The values in this file are placeholders. They will need to be replaced
with the actual resource names from your Google Cloud project.
"""

# ============================================================================
# Google Cloud Project Configuration
# ============================================================================

# Your Google Cloud project ID.
PROJECT_ID = "your-gcp-project-id"

# The location (region) of your GCP resources.
LOCATION = "us-central1"


# ============================================================================
# Vertex AI Search Configuration
# ============================================================================

# Vertex AI Search is used to perform semantic search over unstructured
# documents like vendor docs, municipal policies, and city code.

VERTEX_AI_SEARCH_APP_ID = "your-vertex-ai-search-app-id"
"""
The ID of your Vertex AI Search app. You will create this in the
Google Cloud console. It will be the central point for your
unstructured document search.
"""

# ============================================================================
# Vertex AI Vector Search Configuration
# ============================================================================

# Vertex AI Vector Search is used to find similar past decisions and
# mitigations, allowing the system to "remember" what has worked before.

VECTOR_SEARCH_INDEX_ID = "your-vector-search-index-id"
"""
The ID of your Vector Search index. This index will store the embeddings
of prior city decisions.
"""

VECTOR_SEARCH_INDEX_ENDPOINT_ID = "your-vector-search-index-endpoint-id"
"""
The ID of the index endpoint, which is used to serve online queries
against the vector search index.
"""
