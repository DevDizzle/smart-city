
import json
from orchestration.graph import run_workflow

project_brief = {
  "corridors": ["Mizner Park"],
  "sensors": {
    "alpr": True,
    "video": True,
    "audio": True
  },
  "storage": "hybrid",
  "vendor_hints": ["Ubicquia"]
}

if __name__ == "__main__":
    result = run_workflow(project_brief)
    with open("final_recommendation.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Final recommendation generated and saved to final_recommendation.json")
