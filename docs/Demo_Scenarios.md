# Demo Scenarios

## Scenario A – Likely HOLD
- **Project Brief:**
  ```json
  {
    "zone": "FAU",
    "corridors": ["Glades Rd corridor", "Campus core"],
    "sensors": {
      "alpr": true,
      "video": true,
      "audio": false
    },
    "storage": "cloud",
    "vendor_hints": ["Unknown Vendor"]
  }
  ```
- **Expected Outcome:**
  - `overall_decision`: "HOLD"
  - `needs_human_review`: true
  - **Key Requirement:** A requirement mentioning CJIS should be identified as missing by the Critic.

## Scenario B – MITIGATE
- **Project Brief:**
  ```json
  {
    "zone": "Mizner",
    "corridors": ["Mizner Park"],
    "sensors": {
      "alpr": false,
      "video": true,
      "audio": true
    },
    "storage": "hybrid",
    "vendor_hints": ["Ubicquia UbiHub AP/AI"]
  }
  ```
- **Expected Outcome:**
  - `overall_decision`: "MITIGATE"
  - `needs_human_review`: true
  - **Key Requirement:** A requirement for public notice and retention for video/audio should be identified.

## Scenario C – GO
- **Project Brief:**
  ```json
  {
    "zone": "Downtown",
    "corridors": ["Main Street"],
    "sensors": {
      "alpr": false,
      "video": false,
      "audio": false
    },
    "storage": "edge",
    "vendor_hints": ["Ubicquia UbiHub AP/AI"]
  }
  ```
- **Expected Outcome:**
  - `overall_decision`: "GO"
  - `needs_human_review`: false
  - **Key Requirement:** No major requirements should be flagged as missing.
