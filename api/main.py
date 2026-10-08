from fastapi import FastAPI, HTTPException

from src.investigation.investigation_engine import InvestigationEngine


app = FastAPI(
    title="ORACLE-X API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ORACLE-X API",
    }


@app.post("/investigate/{incident_id}")
def investigate(incident_id: int):
    try:
        engine = InvestigationEngine()
        result = engine.investigate(incident_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Incident {incident_id} not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {exc}",
        )


@app.post("/investigate/{incident_id}/summary")
def investigate_summary(incident_id: int):
    try:
        engine = InvestigationEngine()
        result = engine.investigate(incident_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Incident {incident_id} not found",
            )

        decision = result.get("decision", {})
        validation = result.get("decision_validation", {})
        llm = result.get("llm_interpretation", {})

        interpretation = llm.get("interpretation", {})

        evidence = result.get("evidence", {})
        detection = result.get("detection_evidence", {})

        financial = evidence.get("financial", {})
        customer = evidence.get("customer", {})
        supplier = evidence.get("supplier", {})

        scenario_metrics = {
            "demand": {
                "baseline_daily_orders": detection.get(
                    "baseline_daily_orders"
                ),
                "simulated_daily_orders": detection.get(
                    "simulated_daily_orders"
                ),
                "change_pct": detection.get(
                    "demand_change_pct"
                ),
            },
            "inventory": {
                "baseline_cover_days": detection.get(
                    "baseline_inventory_cover_days"
                ),
                "simulated_cover_days": detection.get(
                    "simulated_inventory_cover_days"
                ),
                "decline_pct": detection.get(
                    "inventory_cover_decline_pct"
                ),
            },
            "financial": {
                "baseline_daily_revenue": financial.get(
                    "baseline_daily_revenue"
                ),
                "current_daily_revenue": financial.get(
                    "current_daily_revenue"
                ),
                "baseline_aov": financial.get(
                    "baseline_aov"
                ),
                "current_aov": financial.get(
                    "current_aov"
                ),
                "change_pct": financial.get(
                    "revenue_change_pct"
                ),
            },
            "customer": {
                "baseline_review_score": customer.get(
                    "baseline_review_score"
                ),
                "current_review_score": customer.get(
                    "current_review_score"
                ),
                "change": customer.get(
                    "review_score_change"
                ),
                "state": customer.get(
                    "customer_state"
                ),
            },
            "supplier": {
                "baseline_risk": supplier.get(
                    "baseline_seller_risk"
                ),
                "current_risk": supplier.get(
                    "current_seller_risk"
                ),
                "pressure_change": supplier.get(
                    "supplier_pressure_change"
                ),
                "state": supplier.get(
                    "supplier_state"
                ),
            },
        }

        return {
            "investigation_id": result.get(
                "investigation_id"
            ),

            "incident": result.get(
                "incident"
            ),

            "decision": {
                "status": decision.get(
                    "decision_status"
                ),
                "recommended_action": decision.get(
                    "recommended_action"
                ),
                "rationale": decision.get(
                    "rationale"
                ),
            },

            "validation": {
                "status": validation.get(
                    "validation_status"
                ),
            },

            "scenario_metrics": scenario_metrics,

            "root_cause_analysis": result.get(
                "root_cause_analysis",
                {},
            ),

            "llm_interpretation": {
                "status": llm.get(
                    "interpretation_status"
                ),
                "model": llm.get(
                    "model"
                ),
                "executive_summary": interpretation.get(
                    "executive_summary"
                ),
                "key_observations": interpretation.get(
                    "key_observations",
                    [],
                ),
                "uncertainty": interpretation.get(
                    "uncertainty",
                    [],
                ),
                "unresolved_questions": interpretation.get(
                    "unresolved_questions",
                    [],
                ),
            },

            "provenance": result.get(
                "provenance"
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Investigation summary failed: {exc}",
        )


@app.get("/investigate/{incident_id}/summary")
def get_investigation_summary(incident_id: int):
    return investigate_summary(incident_id)