"""
VeritAI Smart-City Use Case: OT Security Engineer Agent
"""
from ..rag.vertex_search import search_app, Doc
from ..schemas.common import Evidence, Risk, Requirement
from ..schemas.ot_security import OTSecurityFinding

class OT_SecurityEngineer:
    """
    A specialist agent that analyzes a project brief for OT security implications.
    """

    def analyze_brief(self, project_brief: dict) -> OTSecurityFinding:
        """
        Analyzes a project brief for OT security implications.
        """
        vendor_hints = " ".join(project_brief.get("vendor_hints", []))
        query = f"{vendor_hints} security encryption edge smart streetlight OT security best practices network segmentation"
        
        retrieved_docs: list[Doc] = search_app(query=query, top_k=3)

        evidence = [
            Evidence(
                title=doc.title,
                uri=doc.uri,
                snippet=doc.snippet,
                source=doc.source
            ) for doc in retrieved_docs
        ]

        risks = self._identify_risks(project_brief)
        requirements = self._identify_requirements(project_brief)

        confidence = 0.8 if evidence else 0.3

        return OTSecurityFinding(
            evidence=evidence,
            risks=risks,
            requirements=requirements,
            notes="OT security analysis based on project brief and KB retrieval.",
            confidence=confidence,
        )

    def _identify_risks(self, project_brief: dict) -> list[Risk]:
        """Identifies risks based on the project brief."""
        risks = []
        storage = project_brief.get("storage")
        if storage == "edge" or storage == "hybrid":
            risks.append(Risk(
                risk_id="RISK-OT-001",
                description="Weak or missing encryption at rest on edge devices.",
                severity="High",
                mitigation="Ensure all edge devices support and are configured with strong encryption (e.g., AES-256)."
            ))
        risks.append(Risk(
            risk_id="RISK-OT-002",
            description="Insufficient network segmentation from other city systems.",
            severity="High",
            mitigation="Isolate smart city sensor network from other municipal networks using VLANs or firewalls."
        ))
        return risks

    def _identify_requirements(self, project_brief: dict) -> list[Requirement]:
        """Identifies requirements based on the project brief."""
        requirements = []
        requirements.append(Requirement(
            req_id="REQ-OT-001",
            description="Encryption at rest and in transit must be enabled for all data.",
            is_met=False
        ))
        requirements.append(Requirement(
            req_id="REQ-OT-002",
            description="Network segmentation and access control for devices must be implemented.",
            is_met=False
        ))
        return requirements
