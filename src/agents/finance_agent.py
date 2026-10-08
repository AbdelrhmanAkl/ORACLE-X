class FinanceAgent:
    """
    Deterministic financial interpretation agent.

    Consumes financial evidence already produced by the investigation
    pipeline. It does not query the database, generate business facts,
    or use an LLM.
    """

    def analyze(self, evidence_package):
        financial = evidence_package["evidence"]["financial"]

        revenue_change_pct = financial["revenue_change_pct"]
        baseline_aov = financial["baseline_aov"]
        current_aov = financial["current_aov"]

        if revenue_change_pct > 0:
            financial_status = "REVENUE_INCREASE"
        elif revenue_change_pct < 0:
            financial_status = "REVENUE_DECREASE"
        else:
            financial_status = "REVENUE_STABLE"

        if current_aov > baseline_aov:
            aov_status = "AOV_INCREASE"
        elif current_aov < baseline_aov:
            aov_status = "AOV_DECREASE"
        else:
            aov_status = "AOV_STABLE"

        return {
            "agent": "FinanceAgent",
            "version": "1.0",
            "financial_status": financial_status,
            "revenue_change_pct": revenue_change_pct,
            "aov_status": aov_status,
            "baseline_aov": baseline_aov,
            "current_aov": current_aov,
            "interpretation": {
                "revenue_direction": financial_status,
                "aov_direction": aov_status,
                "revenue_driver_evidence": (
                    "Revenue increased while AOV remained unchanged."
                    if revenue_change_pct > 0
                    and current_aov == baseline_aov
                    else "No deterministic revenue-driver conclusion."
                ),
            },
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "source": "INVESTIGATION_EVIDENCE_PACKAGE",
            },
        }
