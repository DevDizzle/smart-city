"""
UrbanNexus Smart-City Use Case: Vertex AI Search Document Import

This script imports documents from the GCS bucket into the Vertex AI Search data store.
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
LOCATION = "global"  # The location for Vertex AI Search resources.
COLLECTION_ID = "default_collection" # The default collection for data stores.

# GCS bucket for processed documents
PROCESSED_GCS_BUCKET = "urbannexus-smart-city-kb"
PROCESSED_GCS_FOLDER = "processed_docs"

# Path to the generated Vertex AI Search configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "vertex_search_config.json")

# ============================================================================
# Helper Functions
# ============================================================================

def import_documents_from_gcs(
    project_id: str,
    location: str,
    collection_id: str,
    data_store_id: str,
    gcs_uri: str,
):
    """Imports documents from a GCS bucket into a Vertex AI Search data store."""
    print(f"--- Importing documents from {gcs_uri} into data store {data_store_id} ---")

    client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    parent = f"projects/{project_id}/locations/{location}/collections/{collection_id}/dataStores/{data_store_id}/branches/default_branch"

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(input_uris=[gcs_uri], data_schema="document"),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        # Set to `FULL` for a full replacement of existing documents.
        # Set to `INCREMENTAL` to add new documents and update existing ones.
    )

    try:
        operation = client.import_documents(request=request)
        print(f"Waiting for document import operation to complete: {operation.operation.name}")
        response = operation.result()
        print("Document import operation completed.")
        print(f"Full import response: {response}")
        # The success_count and failure_count might be nested or named differently
        # in the v1beta API. We'll inspect the full response to find them.
        # For now, we'll just indicate completion.
        # print(f"Imported {response.success_count} documents successfully.")
        # print(f"Failed to import {response.failure_count} documents.")
        # if response.errors:
        #     print("Errors during import:")
        #     for error in response.errors:
        #         print(f"- {error.message}")
        return response
    except Exception as e:
        print(f"Error during document import: {e}")
        return None

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    The main function that imports documents into the Vertex AI Search data store.
    """
    if not PROJECT_ID:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        return

    print(f"Using project: {PROJECT_ID}")

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at {CONFIG_FILE}. Please run setup_vertex_ai_search.py first.")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    data_store_id = config["data_stores"].keys().__iter__().__next__() # Assuming only one data store for now
    gcs_path = f"gs://{PROCESSED_GCS_BUCKET}/{PROCESSED_GCS_FOLDER}/processed_documents.jsonl"

    import_documents_from_gcs(
        project_id=PROJECT_ID,
        location=LOCATION,
        collection_id=COLLECTION_ID,
        data_store_id=data_store_id,
        gcs_uri=gcs_path,
    )

if __name__ == "__main__":
    main()
