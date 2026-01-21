import json
from dotenv import load_dotenv
from orchestration.graph import run_workflow

load_dotenv()

input_context = {
    "zone_id": "eng_lab_parking",
    "goals": [
        {"type": "Safety", "description": "Increase student safety at night", "priority": "High"},
        {"type": "Energy", "description": "Reduce campus carbon footprint", "priority": "High"},
        {"type": "Connectivity", "description": "Provide outdoor WiFi for students", "priority": "Medium"}
    ],
    "constraints": []
}

if __name__ == "__main__":
    print("Running UrbanNexus V2 Workflow...")
    result = run_workflow(input_context)
    
    with open("final_recommendation_v2.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("Workflow Complete.")
    print(f"Decision: {result['overall_decision']}")
    print(f"Trace ID: {result['trace_id']}")
    
    # Print proposal summary
    if result.get('final_deployment_plan'):
        print("\nProposals:")
        for p in result['final_deployment_plan']:
            print(f"- {p['hardware']['sku']}: {p['value_proposition']}")
