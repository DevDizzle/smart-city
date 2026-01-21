"""
UrbanNexus Smart-City Use Case: Site Viability Agent
"""
import json
import os
from typing import Dict, Any, List
from schemas.common import Zone

class SiteViabilityAgent:
    """
    Simulates the GIS/Infrastructure assessment by reading from a mock database.
    """
    
    def __init__(self, data_path: str = "data/mock_zones.json"):
        self.data_path = data_path
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            # Fallback to empty if file missing
            self.zones_db = {}
            return
            
        try:
            with open(self.data_path, "r") as f:
                data = json.load(f)
                # Index by zone_id
                self.zones_db = {z["zone_id"]: z for z in data.get("zones", [])}
        except Exception as e:
            print(f"Error loading mock zones: {e}")
            self.zones_db = {}

    def run(self, zone_id: str) -> Zone:
        """
        Retrieves the Zone context.
        """
        zone_data = self.zones_db.get(zone_id)
        
        if not zone_data:
            # Return a default/empty zone if not found to prevent crash
            return Zone(
                zone_id=zone_id,
                name="Unknown Zone",
                description="Zone ID not found in GIS database.",
                attributes={},
                coordinates=[]
            )

        return Zone(**zone_data)