"""
VeritAI Smart-City Use Case: Document Conversion and Upload

This script downloads source documents (PDF, HTML), extracts text content,
formats them into JSON Lines, and uploads them to a GCS bucket for Vertex AI Search ingestion.
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from google.cloud import storage
from urllib.parse import urlparse
import markdown
import io
from PyPDF2 import PdfReader

# ============================================================================
# Configuration
# ============================================================================ 

# Your Google Cloud project ID.
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

# GCS bucket for processed documents
PROCESSED_GCS_BUCKET = "veritai-smart-city-kb"
PROCESSED_GCS_FOLDER = "processed_docs"

# Path to the corpus seed markdown file
CORPUS_SEED_FILE = os.path.join(os.path.dirname(__file__), "corpus_seed.md")

# Local directory to store downloaded and processed files temporarily
TEMP_DIR = "temp_processed_docs"

# ============================================================================ 
# Helper Functions
# ============================================================================ 

def download_file(url: str, local_path: str) -> bool:
    """Downloads a file from a URL to a local path."""
    url = url.strip('`') # Strip backticks
    print(f"Downloading {url} to {local_path}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download successful.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def extract_text_from_html(html_path: str) -> str:
    """Extracts text from an HTML file."""
    text = ""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            text = soup.get_text(separator="\n")
    except Exception as e:
        print(f"Error extracting text from HTML {html_path}: {e}")
    return text

def parse_corpus_seed(markdown_content: str) -> list[dict]:
    """Parses the corpus_seed.md content and returns a list of document metadata."""
    docs = []
    lines = markdown_content.splitlines()
    
    # Find the header row to get column indices
    header_line_index = -1
    for i, line in enumerate(lines):
        if "|---" in line:
            header_line_index = i
            break
    
    if header_line_index == -1:
        print("Error: Could not find header in corpus_seed.md")
        return docs

    headers = [h.strip().lower().replace(' ', '_') for h in lines[header_line_index - 1].split('|') if h.strip()]
    
    for line in lines[header_line_index + 1:]:
        if not line.strip() or line.strip().startswith('|--'):
            continue
        
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) == len(headers):
            doc_data = dict(zip(headers, parts))
            # Skip "Broken Links" section
            if doc_data.get("title") == "**Broken Links**":
                break
            if doc_data.get("title") and not doc_data["title"].startswith('**'): # Skip section headers
                docs.append(doc_data)
    return docs

def upload_to_gcs(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Uploads a file to a GCS bucket."""
    print(f"Uploading {source_file_name} to gs://{bucket_name}/{destination_blob_name}...")
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

# ============================================================================ 
# Main Execution
# ============================================================================ 

def main():
    """
    The main function that converts and uploads documents.
    """
    if not PROJECT_ID:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        return

    print(f"Using project: {PROJECT_ID}")

    os.makedirs(TEMP_DIR, exist_ok=True)

    with open(CORPUS_SEED_FILE, "r") as f:
        corpus_seed_content = f.read()
    
    documents_metadata = parse_corpus_seed(corpus_seed_content)

    jsonl_data = []

    for doc_meta in documents_metadata:
        source_url = doc_meta.get("source_url")
        filename = doc_meta.get("filename")
        title = doc_meta.get("title")
        gcs_path_prefix = doc_meta.get("gcs_path")

        if not source_url or not filename or not title or not gcs_path_prefix:
            print(f"Skipping document due to missing metadata: {doc_meta}")
            continue

        filename = filename.strip('`') # Strip backticks from filename
        local_file_path = os.path.join(TEMP_DIR, filename) 
        
        # Download the file
        if not download_file(source_url, local_file_path):
            continue

        extracted_text = ""
        if filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(local_file_path)
        elif filename.endswith(".html"):
            extracted_text = extract_text_from_html(local_file_path)
        elif filename.endswith(".md"): # Assuming markdown files are directly readable
            with open(local_file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
        else:
            print(f"Warning: Unsupported file type for {filename}. Skipping text extraction.")
            continue

        if not extracted_text.strip():
            print(f"Warning: No text extracted from {filename}. Skipping.")
            continue

        # Fix document.id format and implement chunking for large documents
        base_id = os.path.splitext(filename)[0].replace('.', '_') # Replace periods with underscores for valid ID

        # Define a maximum chunk size (e.g., 5000 characters)
        MAX_CHUNK_SIZE = 5000

        if len(extracted_text) > MAX_CHUNK_SIZE:
            # Split into chunks
            chunks = [extracted_text[i:i+MAX_CHUNK_SIZE] for i in range(0, len(extracted_text), MAX_CHUNK_SIZE)]
            for i, chunk_content in enumerate(chunks):
                chunk_id = f"{base_id}_chunk_{i+1}"
                document_json = {
                    "id": chunk_id,
                    "structData": {
                        "title": f"{title} (Part {i+1})",
                        "source_url": source_url,
                        "gcs_path_prefix": gcs_path_prefix,
                        "content": chunk_content,
                        "file_type": os.path.splitext(filename)[1].lstrip('.'),
                        "original_document_id": base_id,
                        "chunk_number": i + 1,
                        "total_chunks": len(chunks),
                    },
                }
                jsonl_data.append(json.dumps(document_json))
        else:
            # Document is small enough, no chunking needed
            document_json = {
                "id": base_id,
                "structData": {
                    "title": title,
                    "source_url": source_url,
                    "gcs_path_prefix": gcs_path_prefix,
                    "content": extracted_text,
                    "file_type": os.path.splitext(filename)[1].lstrip('.'),
                },
            }
            jsonl_data.append(json.dumps(document_json))

    # Write all processed documents to a single JSON Lines file
    processed_jsonl_filename = "processed_documents.jsonl"
    processed_jsonl_local_path = os.path.join(TEMP_DIR, processed_jsonl_filename)
    with open(processed_jsonl_local_path, "w", encoding="utf-8") as f:
        for line in jsonl_data:
            f.write(line + "\n")
    print(f"All processed documents written to {processed_jsonl_local_path}")

    # Upload the JSON Lines file to GCS
    destination_blob_name = f"{PROCESSED_GCS_FOLDER}/{processed_jsonl_filename}"
    upload_to_gcs(PROCESSED_GCS_BUCKET, processed_jsonl_local_path, destination_blob_name)

    print("\nDocument conversion and upload complete.")
    print(f"Processed documents are available at gs://{PROCESSED_GCS_BUCKET}/{destination_blob_name}")

if __name__ == "__main__":
    main()
