.PHONY: install kb.health run.api deploy.api

# ============================================================================
# Dependencies
# ============================================================================
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

# ============================================================================
# Knowledge Base
# ============================================================================
kb.health:
	@echo "Running Knowledge Base Health Check..."
	@export GOOGLE_CLOUD_PROJECT=$(shell gcloud config get-value project) && python -m smart-city.rag.vertex_search

# ============================================================================
# API
# ============================================================================
run.api:
	@echo "Starting API server locally..."
	@uvicorn api.main:app --reload

deploy.api:
	@echo "Deploying API to Cloud Run..."
	@gcloud run deploy veritai-smart-city-api \
		--source . \
		--region us-central1 \
		--allow-unauthenticated \
		--project=$(shell gcloud config get-value project)

