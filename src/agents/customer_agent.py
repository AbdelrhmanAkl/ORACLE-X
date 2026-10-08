class CustomerAgent:
    """
    Deterministic customer interpretation agent.

    Consumes customer evidence already produced by the investigation
    pipeline. It does not query the database, generate business facts,
    or use an LLM.
    """

    def analyze(self, evidence_package):
        customer = evidence_package["evidence"]["customer"]

        baseline_review_score = customer["baseline_review_score"]
        current_review_score = customer["current_review_score"]
        review_score_change = customer["review_score_change"]
        customer_state = customer["customer_state"]

        if current_review_score < baseline_review_score:
            customer_status = "CUSTOMER_EXPERIENCE_DECLINED"
        elif current_review_score > baseline_review_score:
            customer_status = "CUSTOMER_EXPERIENCE_IMPROVED"
        else:
            customer_status = "CUSTOMER_EXPERIENCE_STABLE"

        return {
            "agent": "CustomerAgent",
            "version": "1.0",
            "customer_status": customer_status,
            "baseline_review_score": baseline_review_score,
            "current_review_score": current_review_score,
            "review_score_change": review_score_change,
            "customer_state": customer_state,
            "interpretation": {
                "customer_experience_direction": customer_status,
                "customer_context": (
                    "Simulated customer review score declined."
                    if current_review_score < baseline_review_score
                    else "No deterministic customer experience decline detected."
                ),
            },
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "source": "INVESTIGATION_EVIDENCE_PACKAGE",
            },
        }
