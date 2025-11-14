"""
VeritAI Smart-City Use Case: Privacy Counsel Agent
"""
from ..rag.vertex_search import search_app, Doc
from ..schemas.common import Evidence, Risk, Requirement
from ..schemas.privacy import PrivacyFinding

class PrivacyCounsel:
    """
    A specialist agent that analyzes a project brief for privacy implications.
    """

    def analyze_brief(self, project_brief: dict) -> PrivacyFinding:
        """
        Analyzes a project brief for privacy implications.
        """
        query = "Florida Sunshine Law video surveillance retention public records obligations for camera footage Florida privacy impact assessment public surveillance"
        
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

        confidence = 0.9 if evidence else 0.4

        return PrivacyFinding(
            evidence=evidence,
            risks=risks,
            requirements=requirements,
            notes="Privacy analysis based on project brief and KB retrieval.",
            confidence=confidence,
        )

    def _identify_risks(self, project_brief: dict) -> list[Risk]:
        """Identifies risks based on the project brief."""
        risks = []
        sensors = project_brief.get("sensors", {})
        if sensors.get("video") or sensors.get("audio"):
            risks.append(Risk(
                risk_id="RISK-PRIV-001",
                description="Over-collection of personally identifying data.",
                severity="Medium",
                mitigation="Implement data minimization techniques and PII redaction."
            ))
            risks.append(Risk(
                risk_id="RISK-PRIV-002",
                description="Insufficient notice to the public about data collection.",
                severity="High",
                mitigation="Post clear and conspicuous notices at all sensor locations."
            ))
        return risks

    def _identify_requirements(self, project_brief: dict) -> list[Requirement]:
        """Identifies requirements based on the project brief."""
        requirements = []
        sensors = project_brief.get("sensors", {})
        if sensors.get("video") or sensors.get("audio"):
            requirements.append(Requirement(
                req_id="REQ-PRIV-001",
                description="A publicly posted notice is required where sensors are deployed.",
                is_met=False
            ))
            requirements.append(Requirement(
                req_id="REQ-PRIV-002",
                description="A published retention schedule for video/ALPR/audio data is required.",
                is_met=False
            ))
        return requirements
