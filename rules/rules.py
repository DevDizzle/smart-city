"""
UrbanNexus Smart-City Use Case: Governance Rules

This module defines the specific governance rules for the "Go/No-Go for
Smart-City Deployments" use case. These rules are built using the core
ProtocolRule class from the urbannexus-core layer.
"""

from urbannexus.protocol.rules import ProtocolRule, Severity

# ============================================================================
# Smart-City Governance Rules
# ============================================================================

class SmartCityRules:
    """
    A collection of all governance rules specific to the smart-city use case.
    """

    # --- Rule: CJIS Compliance Trigger ---
    CJIS_TRIGGER = ProtocolRule(
        rule_id="SC-CJIS-001",
        description="If the solution involves Automated License Plate Readers (ALPR) or other public safety data, a CJIS compliance path is required.",
        # This condition checks if the 'public_safety' agent's findings mention 'ALPR'.
        trigger_condition="'alpr' in state.get('publicsafetyspecialist', {}).get('findings', '').lower()",
        required_action="The Validator must confirm that a CJIS compliance plan is in place.",
        override_allowed=False,
        severity_level=Severity.HIGH
    )

    # --- Rule: Sunshine Law (Public Records) Trigger ---
    SUNSHINE_LAW_TRIGGER = ProtocolRule(
        rule_id="SC-SUNSHINE-001",
        description="If deployed in a municipality subject to public records laws (e.g., Florida Sunshine Law), the audit trace must be FOIA-ready.",
        # This condition could be based on a 'location' field in the initial proposal.
        trigger_condition="'florida' in state.get('proposal', {}).get('location', '').lower()",
        required_action="The Validator must ensure the audit trace is configured for public disclosure and that PII is properly redacted.",
        override_allowed=False,
        severity_level=Severity.MEDIUM
    )

    # --- Rule: NIST AI RMF - Community Notice for PII ---
    NIST_RMF_COMMUNITY_NOTICE = ProtocolRule(
        rule_id="SC-NIST-RMF-001",
        description="If cameras or microphones are used to collect Personally Identifiable Information (PII), a community notice and privacy impact assessment are required.",
        # This condition checks the findings of the 'privacy' agent.
        trigger_condition="state.get('privacycounsel', {}).get('findings', {}).get('collects_pii', False) and ('camera' in state.get('proposal', {}).get('hardware', []) or 'microphone' in state.get('proposal', {}).get('hardware', []))",
        required_action="The Validator must confirm that a community notice plan and a privacy impact assessment have been completed.",
        override_allowed=False,
        severity_level=Severity.HIGH
    )

    @classmethod
    def get_all_rules(cls) -> list[ProtocolRule]:
        """Returns a list of all rules for the smart-city use case."""
        return [
            cls.CJIS_TRIGGER,
            cls.SUNSHINE_LAW_TRIGGER,
            cls.NIST_RMF_COMMUNITY_NOTICE,
        ]
