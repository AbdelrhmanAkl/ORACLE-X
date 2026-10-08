class DecisionEngine:
    """
    Deterministic decision layer for ORACLE-X.

    Responsibilities:
    - Evaluate explicit decision rules.
    - Produce an auditable operational decision.
    - Preserve evidence provenance and uncertainty.
    - Never invent business facts.
    - Never claim causal certainty.
    - Never use an LLM.
    """

    VERSION = "1.0"

    def decide(
        self,
        evidence_synthesis,
        debate,
    ):
        inventory_signal = None

        for signal in evidence_synthesis["strongest_signals"]:
            if signal["signal"] == "Inventory coverage declined":
                inventory_signal = signal
                break

        if inventory_signal is None:
            return {
                "decision_status": "INSUFFICIENT_EVIDENCE",
                "recommended_action": None,
                "rationale": "Required inventory evidence is unavailable.",
                "supporting_evidence": [],
                "constraints": {
                    "deterministic": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "causal_certainty_claimed": False,
                },
                "provenance": {
                    "source": "EVIDENCE_SYNTHESIS",
                    "debate_status": debate["debate_status"],
                    "recommendation_source": "DETERMINISTIC_DECISION_RULE",
                },
                "version": self.VERSION,
            }

        inventory_evidence = inventory_signal["evidence"]

        if (
            evidence_synthesis["assessment"]["causal_certainty"]
            == "NOT_ESTABLISHED"
            and debate["debate_status"]
            == "CONSENSUS_WITH_UNRESOLVED_QUESTIONS"
        ):
            return {
                "decision_status": "ACTIONABLE",
                "recommended_action": (
                    "Prioritize inventory protection and monitor "
                    "demand and supplier conditions."
                ),
                "rationale": (
                    "Simulated inventory coverage declined materially "
                    "while simulated business activity increased. "
                    "The evidence supports a protective operational "
                    "response, but does not establish a single causal "
                    "root cause."
                ),
                "supporting_evidence": [
                    {
                        "signal": "Inventory coverage declined",
                        "evidence": inventory_evidence,
                        "evidence_type": inventory_signal["evidence_type"],
                    },
                    {
                        "signal": "Debate status",
                        "evidence": debate["debate_status"],
                        "evidence_type": "DETERMINISTIC",
                    },
                ],
                "constraints": {
                    "deterministic": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "causal_certainty_claimed": False,
                },
                "provenance": {
                    "source": "EVIDENCE_SYNTHESIS_AND_DEBATE",
                    "recommendation_source": "DETERMINISTIC_DECISION_RULE",
                    "inventory_evidence": "MODEL_DERIVED_AND_SIMULATED",
                    "scenario_context": "SIMULATED",
                },
                "version": self.VERSION,
            }

        return {
            "decision_status": "MONITOR",
            "recommended_action": (
                "Continue monitoring inventory and demand conditions."
            ),
            "rationale": (
                "Available evidence does not satisfy the configured "
                "decision condition."
            ),
            "supporting_evidence": [],
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "causal_certainty_claimed": False,
            },
            "provenance": {
                "source": "EVIDENCE_SYNTHESIS_AND_DEBATE",
                "recommendation_source": "DETERMINISTIC_DECISION_RULE",
            },
            "version": self.VERSION,
        }