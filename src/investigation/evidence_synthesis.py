class EvidenceSynthesizer:
    """
    Deterministic evidence synthesis layer for ORACLE-X.

    Responsibilities:
    - Combine investigation evidence, agent analysis, and RCA candidates.
    - Identify cross-agent agreement and unresolved conflicts.
    - Preserve evidence provenance and uncertainty.
    - Never invent business facts.
    - Never claim causal certainty.
    - Never generate recommendations.
    - Never use an LLM.
    """

    def synthesize(
        self,
        evidence_package,
        agent_analysis,
        root_cause_analysis,
    ):
        incident = evidence_package["incident"]
        evidence = evidence_package["evidence"]

        strongest_signals = [
            {
                "signal": "Commercial activity increased",
                "source": "FinanceAgent",
                "evidence": (
                    f"Revenue increased by "
                    f"{agent_analysis['finance']['revenue_change_pct']:.2f}% "
                    f"while AOV remained stable."
                ),
                "evidence_type": "SIMULATED",
            },
            {
                "signal": "Operational demand increased",
                "source": "OperationsAgent",
                "evidence": (
                    f"Simulated orders increased from "
                    f"{agent_analysis['operations']['baseline_orders']:.2f} "
                    f"to "
                    f"{agent_analysis['operations']['current_orders']:.2f}."
                ),
                "evidence_type": "SIMULATED",
            },
            {
                "signal": "Inventory coverage declined",
                "source": "InvestigationEvidence",
                "evidence": (
                    f"Inventory cover declined from "
                    f"{evidence['inventory']['baseline_cover_days']:.2f} "
                    f"to "
                    f"{evidence['inventory']['current_cover_days']:.2f} days."
                ),
                "evidence_type": "MODEL_DERIVED_AND_SIMULATED",
            },
            {
                "signal": "Supplier risk increased",
                "source": "RiskAgent",
                "evidence": (
                    f"Seller risk increased by "
                    f"{evidence['supplier']['supplier_pressure_change']:.2f} "
                    f"risk points."
                ),
                "evidence_type": "SIMULATED",
            },
            {
                "signal": "Customer experience declined",
                "source": "CustomerAgent",
                "evidence": (
                    f"Review score declined by "
                    f"{abs(evidence['customer']['review_score_change']):.2f} "
                    f"points."
                ),
                "evidence_type": "SIMULATED_DOWNSTREAM_IMPACT",
            },
        ]

        candidate_assessment = []

        for candidate in root_cause_analysis["candidate_causes"]:
            candidate_assessment.append(
                {
                    "candidate_cause": candidate["candidate_cause"],
                    "confidence": candidate["confidence"],
                    "evidence_for": candidate["evidence_for"],
                    "evidence_against": candidate["evidence_against"],
                    "evidence_type": candidate["evidence_type"],
                    "causal_certainty": "NOT_ESTABLISHED",
                }
            )

        finance = agent_analysis["finance"]
        operations = agent_analysis["operations"]
        risk = agent_analysis["risk"]
        customer = agent_analysis["customer"]

        consensus = []

        if (
            finance["financial_status"] == "REVENUE_INCREASE"
            and operations["order_status"] == "ORDERS_INCREASED"
        ):
            consensus.append(
                {
                    "topic": "Demand and commercial activity",
                    "agreement": True,
                    "agents": ["FinanceAgent", "OperationsAgent"],
                    "finding": (
                        "Finance and Operations both identify increased "
                        "simulated business activity."
                    ),
                }
            )

        if (
            risk["supplier_status"] == "SUPPLIER_RISK_INCREASED"
            and risk["customer_status"] == "CUSTOMER_RISK_INCREASED"
            and customer["customer_status"]
            == "CUSTOMER_EXPERIENCE_DECLINED"
        ):
            consensus.append(
                {
                    "topic": "Risk and customer deterioration",
                    "agreement": True,
                    "agents": ["RiskAgent", "CustomerAgent"],
                    "finding": (
                        "Risk and Customer analysis both identify increased "
                        "simulated supplier/customer pressure."
                    ),
                }
            )

        unresolved_questions = [
            (
                "Does the simulated demand increase represent a historically "
                "unusual demand event?"
            ),
            (
                "Is inventory pressure an initiating factor or a consequence "
                "of the simulated demand increase?"
            ),
            (
                "Does supplier pressure represent an observed operational "
                "relationship or only a controlled simulation condition?"
            ),
            (
                "Can the simulated customer deterioration be attributed to "
                "the demand and inventory conditions without additional "
                "historical evidence?"
            ),
        ]

        return {
            "assessment": {
                "incident_id": incident["incident_id"],
                "incident_type": incident["incident_type"],
                "severity": incident["severity"],
                "overall_assessment": (
                    "The available evidence shows a simulated increase in "
                    "demand and commercial activity occurring alongside "
                    "declining inventory coverage and simulated supplier "
                    "and customer pressure. The evidence does not establish "
                    "a single causal root."
                ),
                "causal_certainty": "NOT_ESTABLISHED",
            },
            "strongest_signals": strongest_signals,
            "candidate_assessment": candidate_assessment,
            "cross_agent_consensus": consensus,
            "unresolved_questions": unresolved_questions,
            "provenance": {
                "historical_data": "OBSERVED_HISTORICAL",
                "inventory_level_and_coverage": "MODEL_DERIVED",
                "scenario_changes": "SIMULATED",
                "agent_analysis": "DETERMINISTIC",
                "root_cause_analysis": "DETERMINISTIC_RCA",
                "llm_used": False,
                "business_facts_generated": False,
                "causal_certainty_claimed": False,
                "recommendation_generated": False,
            },
        }
