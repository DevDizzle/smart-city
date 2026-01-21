# UrbanNexus MVP Runbook

## Overview
UrbanNexus evaluates smart-streetlight AI deployments and returns GO / MITIGATE / HOLD with an audit trace.

## Prerequisites
- Google Cloud project with the following enabled:
  - Vertex AI Search
  - Cloud Run
  - BigQuery
- A BigQuery dataset named `urbannexus_audit` for protocol events.
- A service account with permissions for Vertex AI Search and BigQuery.

## Configuration
- Set the `GOOGLE_CLOUD_PROJECT` environment variable to your Google Cloud project ID.
- Ensure your Vertex AI Search engine is configured and the details are in `smart-city/rag/config/vertex_search_config.json`.

## Deployment
To deploy the API to Cloud Run, run the following command from the `smart-city` directory:
```bash
make deploy.api
```
This will create a Cloud Run service named `urbannexus-smart-city-api`.

## Smoke Tests
1.  **Check Knowledge Base Health:**
    ```bash
    make kb.health
    ```
2.  **Analyze a Scenario:**
    Use `curl` or the FastAPI Swagger UI to send a POST request to the `/analyze` endpoint.
    ```bash
    curl -X POST "http://<your-cloud-run-url>/analyze" \
    -H "Content-Type: application/json" \
    -d '{
      "zone": "Mizner",
      "corridors": ["Mizner Park"],
      "sensors": {
        "alpr": false,
        "video": true,
        "audio": true
      },
      "storage": "hybrid",
      "vendor_hints": ["Ubicquia UbiHub AP/AI"]
    }'
    ```
3.  **Retrieve a Trace:**
    From the response of the `/analyze` endpoint, get the `trace_id` and use it to retrieve the trace.
    ```bash
    curl "http://<your-cloud-run-url>/trace/<your-trace-id>"
    ```

## Basic Troubleshooting
- **Empty retrieval results:** Check the configuration of your Vertex AI Search app.
- **Permission errors:** Check the IAM permissions of your Cloud Run service account.
- **Trace lookup fails:** Ensure the `trace_id` is correct and that the service is running.

## Querying Logs in BigQuery

To query the protocol events in BigQuery, you can use the following SQL query. Make sure to replace `your-project-id`, `urbannexus_audit`, and `protocol_events_table` with your actual project ID, dataset, and table names.

```sql
SELECT
  *
FROM
  `your-project-id.urbannexus_audit.protocol_events_table`
WHERE
  jsonPayload.session_id = "your-trace-id"
ORDER BY
  timestamp
```
