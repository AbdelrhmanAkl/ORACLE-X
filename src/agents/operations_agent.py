class OperationsAgent:
    """
    Deterministic operational interpretation agent.

    Consumes operational evidence already produced by the investigation
    pipeline. It does not query the database, generate business facts,
    or use an LLM.
    """

    def analyze(self, evidence_package):
        operational = evidence_package["evidence"]["operational"]

        baseline_orders = operational["baseline_orders"]
        current_orders = operational["current_orders"]

        if current_orders > baseline_orders:
            order_status = "ORDERS_INCREASED"
        elif current_orders < baseline_orders:
            order_status = "ORDERS_DECREASED"
        else:
            order_status = "ORDERS_STABLE"

        return {
            "agent": "OperationsAgent",
            "version": "1.0",
            "order_status": order_status,
            "baseline_orders": baseline_orders,
            "current_orders": current_orders,
            "simulation_status": operational[
                "simulation_status"
            ],
            "event_id": operational["event_id"],
            "snapshot_id": operational["snapshot_id"],
            "interpretation": {
                "order_direction": order_status,
                "operational_context": (
                    "Simulated order volume increased."
                    if current_orders > baseline_orders
                    else "No deterministic order-volume increase detected."
                ),
            },
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "source": "INVESTIGATION_EVIDENCE_PACKAGE",
            },
        }
