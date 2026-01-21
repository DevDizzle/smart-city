"""
UrbanNexus Smart-City Use Case: Vertex AI Search Setup

This script programmatically creates the necessary Vertex AI Search resources
(Data Stores and a Search App) for the UrbanNexus project.

This is part of Step D in the project plan.
"""

import os
import json
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.client_options import ClientOptions

# ============================================================================
# Configuration
# ============================================================================

# Your Google Cloud project ID.
# This will be read from the environment variable GOOGLE_CLOUD_PROJECT.
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "global"  # The location for Vertex AI Search resources.
COLLECTION_ID = "default_collection" # The default collection for data stores.

ENGINE_ID = "urbannexus-smart-city-engine"
ENGINE_DISPLAY_NAME = "UrbanNexus Smart City Engine"

# A list of the data stores we need to create.
DATA_STORES_TO_CREATE = [
    {
        "id": "urbannexus-smart-city-kb-ds",
        "display_name": "UrbanNexus Smart City Knowledge Base",
        "gcs_path": "gs://urbannexus-smart-city-kb/",
    },
]

# ============================================================================
# Helper Functions
# ============================================================================

def create_data_store(
    client: discoveryengine.DataStoreServiceClient,
    parent_path: str,
    data_store_id: str,
    display_name: str,
) -> discoveryengine.DataStore:
    """Creates a data store in Vertex AI Search."""
    print(f"--- Creating data store: {display_name} ---")
    data_store = discoveryengine.DataStore( # Corrected
        display_name=display_name,
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config="NO_CONTENT",
    )

    try:
        operation = client.create_data_store(
            parent=parent_path,
            data_store=data_store,
            data_store_id=data_store_id,
        )
        print(f"Waiting for operation to complete: {operation.operation.name}")
        response = operation.result()
        print(f"Data store created: {response.name}")
        return response
    except Exception as e:
        print(f"Error creating data store {data_store_id}: {e}")
        # It's possible the data store already exists. We can try to get it.
        try:
            print(f"Attempting to get existing data store: {data_store_id}")
            data_store_path = client.data_store_path(
                project=PROJECT_ID, location=LOCATION, data_store=data_store_id
            )
            return client.get_data_store(name=data_store_path)
        except Exception as get_e:
            print(f"Could not get existing data store {data_store_id}: {get_e}")
            return None

def create_engine_app(
    project_id: str,
    location: str,
    collection_id: str,
    engine_id: str,
    display_name: str,
    data_store_names: list[str],
) -> discoveryengine.Engine:
    """Creates a Discovery Engine search app (engine)."""
    print(f"--- Creating Engine App: {display_name} ---")
    
    client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    client = discoveryengine.EngineServiceClient(client_options=client_options)

    parent = f"projects/{project_id}/locations/{location}/collections/{collection_id}"
    
    engine = discoveryengine.Engine( # Corrected
        display_name=display_name,
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        data_store_ids=[ds.split('/')[-1] for ds in data_store_names],
    )

    try:
        request = discoveryengine.CreateEngineRequest(
            parent=parent,
            engine=engine,
            engine_id=engine_id,
        )
        operation = client.create_engine(request=request)
        print(f"Waiting for operation to complete: {operation.operation.name}")
        response = operation.result()
        print(f"Engine App created: {response.name}")
        return response
    except Exception as e:
        print(f"Error creating Engine App {engine_id}: {e}")
        # It's possible the Engine App already exists. We can try to get it.
        try:
            print(f"Attempting to get existing Engine App: {engine_id}")
            engine_path = client.engine_path(
                project=project_id, location=location, collection=collection_id, engine=engine_id
            )
            return client.get_engine(name=engine_path)
        except Exception as get_e:
            print(f"Could not get existing Engine App {engine_id}: {get_e}")
            return None

def write_vertex_search_config(
    output_file: str,
    project_id: str,
    location: str,
    collection_id: str,
    data_stores: dict,
    engine_app: discoveryengine.Engine,
):
    """Writes the Vertex AI Search configuration to a JSON file."""
    print(f"--- Writing Vertex AI Search configuration to {output_file} ---")
    config = {
        "project_id": project_id,
        "location": location,
        "collection_id": collection_id,
        "data_stores": {ds_id: ds_name for ds_id, ds_name in data_stores.items()},
        "search_app": {
            "id": engine_app.name.split('/')[-1],
            "name": engine_app.name,
            "display_name": engine_app.display_name,
            "data_store_ids": list(engine_app.data_store_ids), # Convert to list here
        }
    }
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)
    print("Configuration written successfully.")

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    The main function that creates all the necessary Vertex AI Search resources.
    """
    if not PROJECT_ID:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        return

    print(f"Using project: {PROJECT_ID}")

    # Initialize DataStoreServiceClient
    ds_client = discoveryengine.DataStoreServiceClient()
    ds_parent_path = ds_client.collection_path(PROJECT_ID, LOCATION, COLLECTION_ID)

    created_data_stores = {}

    for ds_config in DATA_STORES_TO_CREATE:
        data_store = create_data_store(
            client=ds_client,
            parent_path=ds_parent_path,
            data_store_id=ds_config["id"],
            display_name=ds_config["display_name"],
        )
        if data_store:
            created_data_stores[ds_config["id"]] = data_store.name
            # In a real implementation, we would also link the GCS path here.
            # This requires a separate API call to import documents.
            print(f"TODO: Link GCS path {ds_config['gcs_path']} to data store {data_store.name}")

    print("\n--- Summary of Created Data Stores ---")
    for ds_id, ds_name in created_data_stores.items():
        print(f"  {ds_id}: {ds_name}")

    # Create Engine App
    engine_app = create_engine_app(
        project_id=PROJECT_ID,
        location=LOCATION,
        collection_id=COLLECTION_ID,
        engine_id=ENGINE_ID,
        display_name=ENGINE_DISPLAY_NAME,
        data_store_names=list(created_data_stores.values()),
    )

    if engine_app:
        # Write configuration to file
        output_dir = os.path.join(os.path.dirname(__file__), "config")
        output_file = os.path.join(output_dir, "vertex_search_config.json")
        write_vertex_search_config(
            output_file=output_file,
            project_id=PROJECT_ID,
            location=LOCATION,
            collection_id=COLLECTION_ID,
            data_stores=created_data_stores,
            engine_app=engine_app,
        )
    else:
        print("Warning: Engine App was not created. Skipping config file generation.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
