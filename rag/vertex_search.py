"""
UrbanNexus Smart-City Use Case: Vertex AI Search Retrieval Tool

This script provides a function to query the Vertex AI Search App and retrieve
relevant documents.
"""

import os
import json
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.client_options import ClientOptions

# ============================================================================
# Configuration
# ============================================================================

# Your Google Cloud project ID.
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

# Path to the generated Vertex AI Search configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "vertex_search_config.json")

# ============================================================================
# Data Structures
# ============================================================================

class Doc:
    """Represents a retrieved document."""
    def __init__(self, title: str, uri: str, snippet: str, source: str):
        self.title = title
        self.uri = uri
        self.snippet = snippet
        self.source = source

    def __repr__(self):
        return f"Doc(title='{self.title}', uri='{self.uri}', snippet='{self.snippet[:50]}...', source='{self.source}')"

# ============================================================================
# Retrieval Function
# ============================================================================

def search_app(query: str, top_k: int = 8) -> list[Doc]:
    """
    Queries the Vertex AI Search App and retrieves relevant documents.

    Args:
        query: The search query string.
        top_k: The maximum number of documents to retrieve.

    Returns:
        A list of Doc objects representing the retrieved documents.
    """
    if not PROJECT_ID:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        return []

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at {CONFIG_FILE}. Please run setup_vertex_ai_search.py first.")
        return []

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    location = config["location"]
    collection_id = config["collection_id"]
    engine_id = config["search_app"]["id"]

    client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    serving_config = (
        f"projects/{PROJECT_ID}/locations/{location}/collections/{collection_id}/"
        f"engines/{engine_id}/servingConfigs/default_search"
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=top_k,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)

    retrieved_docs = []
    for result in response.results:
        document = result.document
        
        # Extract relevant fields from document.derived_struct_data or document.struct_data
        title = document.derived_struct_data.get("title") or document.struct_data.get("title", "No Title")
        uri = document.derived_struct_data.get("link") or document.struct_data.get("source_url", "No URI")
        snippet = document.derived_struct_data.get("snippet") or document.struct_data.get("content", "No Snippet")
        source = document.derived_struct_data.get("source") or document.struct_data.get("gcs_path_prefix", "No Source")

        retrieved_docs.append(Doc(title=title, uri=uri, snippet=snippet, source=source))

    return retrieved_docs

# ============================================================================
# Example Usage (for testing)
# ============================================================================

if __name__ == "__main__":
    # Set your project ID as an environment variable before running
    # export GOOGLE_CLOUD_PROJECT=your-project-id

    sample_query = "Sunshine Law video retention"
    print(f"Searching for: '{sample_query}'")
    results = search_app(sample_query, top_k=3)

    if results:
        for i, doc in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"Title: {doc.title}")
            print(f"URI: {doc.uri}")
            print(f"Snippet: {doc.snippet[:200]}...") # Truncate snippet for display
            print(f"Source: {doc.source}")
    else:
        print("No results found.")
