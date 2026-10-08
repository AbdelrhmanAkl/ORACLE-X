class DecisionValidator:
    """
    Deterministic validation layer for ORACLE-X decisions.

    Responsibilities:
    - Validate decision structure.
    - Validate decision provenance and constraints.
    - Ensure supporting evidence exists for actionable decisions.
    - Prevent unsupported causal certainty.
    - Never generate business facts.
    - Never use an LLM.
    """

    VERSION = "1.0"

    VALID_STATUSES = {
        "ACTIONABLE",
        "MONITOR",
        "INSUFFICIENT_EVIDENCE",
    }

    def validate(self, decision):
        errors = []

        decision_status = decision.get("decision_status")
        recommended_action = decision.get("recommended_action")
        supporting_evidence = decision.get("supporting_evidence")
        constraints = decision.get("constraints", {})
        provenance = decision.get("provenance", {})

        if decision_status not in self.VALID_STATUSES:
            errors.append(
                "Decision status is invalid."
            )

        if decision_status == "ACTIONABLE":
            if not recommended_action:
                errors.append(
                    "Actionable decision must contain a recommended action."
                )

            if not supporting_evidence:
                errors.append(
                    "Actionable decision must contain supporting evidence."
                )

        if constraints.get("deterministic") is not True:
            errors.append(
                "Decision must be deterministic."
            )

        if constraints.get("llm_used") is not False:
            errors.append(
                "Decision must not use an LLM."
            )

        if constraints.get("business_facts_generated") is not False:
            errors.append(
                "Decision must not generate business facts."
            )

        if constraints.get("causal_certainty_claimed") is not False:
            errors.append(
                "Decision must not claim causal certainty."
            )

        if provenance.get("recommendation_source") != (
            "DETERMINISTIC_DECISION_RULE"
        ):
            errors.append(
                "Recommendation source must be a deterministic decision rule."
            )

        validation_status = (
            "VALID"
            if not errors
            else "INVALID"
        )

        return {
            "validation_status": validation_status,
            "decision_status": decision_status,
            "errors": errors,
            "checks": {
                "status_valid": decision_status in self.VALID_STATUSES,
                "action_present": bool(recommended_action),
                "supporting_evidence_present": bool(
                    supporting_evidence
                ),
                "deterministic": (
                    constraints.get("deterministic") is True
                ),
                "llm_used": constraints.get("llm_used"),
                "business_facts_generated": constraints.get(
                    "business_facts_generated"
                ),
                "causal_certainty_claimed": constraints.get(
                    "causal_certainty_claimed"
                ),
                "recommendation_source_valid": (
                    provenance.get("recommendation_source")
                    == "DETERMINISTIC_DECISION_RULE"
                ),
            },
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "causal_certainty_claimed": False,
            },
            "provenance": {
                "source": "DECISION_ENGINE",
                "validation_method": "DETERMINISTIC_RULES",
            },
            "version": self.VERSION,
        }