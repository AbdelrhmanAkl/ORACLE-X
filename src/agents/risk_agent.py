class RiskAgent:
    """
    Deterministic risk interpretation agent.

    Consumes supplier and customer risk evidence already produced by the
    investigation pipeline. It does not query the database, generate
    business facts, or use an LLM.
    """

    def analyze(self, evidence_package):
        supplier = evidence_package["evidence"]["supplier"]
        customer = evidence_package["evidence"]["customer"]

        baseline_supplier_risk = supplier["baseline_seller_risk"]
        current_supplier_risk = supplier["current_seller_risk"]
        supplier_pressure_change = supplier["supplier_pressure_change"]

        baseline_review_score = customer["baseline_review_score"]
        current_review_score = customer["current_review_score"]
        review_score_change = customer["review_score_change"]

        if current_supplier_risk > baseline_supplier_risk:
            supplier_status = "SUPPLIER_RISK_INCREASED"
        elif current_supplier_risk < baseline_supplier_risk:
            supplier_status = "SUPPLIER_RISK_DECREASED"
        else:
            supplier_status = "SUPPLIER_RISK_STABLE"

        if current_review_score < baseline_review_score:
            customer_status = "CUSTOMER_RISK_INCREASED"
        elif current_review_score > baseline_review_score:
            customer_status = "CUSTOMER_RISK_DECREASED"
        else:
            customer_status = "CUSTOMER_RISK_STABLE"

        return {
            "agent": "RiskAgent",
            "version": "1.0",
            "supplier_status": supplier_status,
            "customer_status": customer_status,
            "baseline_supplier_risk": baseline_supplier_risk,
            "current_supplier_risk": current_supplier_risk,
            "supplier_pressure_change_pct": supplier_pressure_change,
            "baseline_review_score": baseline_review_score,
            "current_review_score": current_review_score,
            "review_score_change": review_score_change,
            "interpretation": {
                "supplier_risk_direction": supplier_status,
                "customer_risk_direction": customer_status,
                "risk_context": (
                    "Supplier risk increased while customer review score declined."
                    if current_supplier_risk > baseline_supplier_risk
                    and current_review_score < baseline_review_score
                    else "No deterministic combined supplier and customer risk conclusion."
                ),
            },
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "source": "INVESTIGATION_EVIDENCE_PACKAGE",
            },
        }
