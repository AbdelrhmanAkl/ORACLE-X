class DebateEngine:
    """
    Deterministic debate layer for ORACLE-X.

    Responsibilities:
    - Compare independent agent findings.
    - Identify agreement and disagreement.
    - Preserve unresolved questions.
    - Avoid causal certainty.
    - Avoid recommendations.
    - Never generate business facts.
    - Never use an LLM.
    """

    VERSION = "1.0"

    def debate(
        self,
        agent_analysis,
        root_cause_analysis,
        evidence_synthesis,
    ):
        finance = agent_analysis["finance"]
        operations = agent_analysis["operations"]
        risk = agent_analysis["risk"]
        customer = agent_analysis["customer"]

        agreements = []
        disagreements = []

        if (
            finance["financial_status"] == "REVENUE_INCREASE"
            and operations["order_status"] == "ORDERS_INCREASED"
        ):
            agreements.append(
                {
                    "topic": "Commercial and operational activity",
                    "agents": ["FinanceAgent", "OperationsAgent"],
                    "finding": (
                        "Both agents identify increased simulated business "
                        "activity."
                    ),
                    "evidence_type": "SIMULATED",
                }
            )

        if (
            risk["supplier_status"] == "SUPPLIER_RISK_INCREASED"
            and customer["customer_status"]
            == "CUSTOMER_EXPERIENCE_DECLINED"
        ):
            agreements.append(
                {
                    "topic": "Supplier and customer pressure",
                    "agents": ["RiskAgent", "CustomerAgent"],
                    "finding": (
                        "Both analyses identify simulated supplier pressure "
                        "and customer experience deterioration."
                    ),
                    "evidence_type": "SIMULATED",
                }
            )

        if not root_cause_analysis["validation"]["causal_certainty_claimed"]:
            disagreements.append(
                {
                    "topic": "Root cause certainty",
                    "finding": (
                        "The evidence does not establish a single causal "
                        "root cause."
                    ),
                    "status": "UNRESOLVED",
                }
            )

        unresolved_questions = list(
            evidence_synthesis["unresolved_questions"]
        )

        return {
            "debate_status": (
                "CONSENSUS_WITH_UNRESOLVED_QUESTIONS"
                if agreements
                else "UNRESOLVED"
            ),
            "agreements": agreements,
            "disagreements": disagreements,
            "unresolved_questions": unresolved_questions,
            "provenance": {
                "source": "INVESTIGATION_EVIDENCE_PACKAGE",
                "agent_analysis": "DETERMINISTIC",
                "root_cause_analysis": "DETERMINISTIC_RCA",
                "evidence_synthesis": "DETERMINISTIC",
                "llm_used": False,
                "business_facts_generated": False,
                "causal_certainty_claimed": False,
                "recommendation_generated": False,
            },
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "causal_certainty_claimed": False,
                "recommendation_generated": False,
            },
            "version": self.VERSION,
        }