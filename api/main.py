import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from src.intelligence.summary_translator import SummaryTranslator
from src.investigation.investigation_engine import InvestigationEngine


logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"en", "ar"}


def _normalize_language(lang):
    normalized = (lang or "en").strip().lower()

    if normalized not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported language. "
                f"Use one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}."
            ),
        )

    return normalized


def _translate_summary(summary, language):
    """
    Translate the text fields of a summary. Facts, numbers and decisions are
    never modified. Translation problems never fail the request: the English
    summary is returned with translation.status set to FAILED.
    """
    try:
        translator = SummaryTranslator()
    except Exception as exc:
        summary["language"] = "en"
        summary["translation"] = {
            "status": "FAILED",
            "language": language,
            "reason": str(exc)[:160],
        }
        return summary

    return translator.translate_summary(summary, language)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.getenv("ORACLE_X_DB_URL")
    db_sha256 = os.getenv("ORACLE_X_DB_SHA256")

    if not db_url or not db_sha256:
        raise RuntimeError(
            "Missing required environment variables: "
            "ORACLE_X_DB_URL and ORACLE_X_DB_SHA256."
        )

    from scripts.bootstrap_deployment_db import (
        main as bootstrap_database,
    )

    logger.info("Initializing deployment database.")
    bootstrap_database()
    logger.info("Deployment database initialization completed.")

    yield


app = FastAPI(
    title="ORACLE-X API",
    version="1.0.0",
    lifespan=lifespan,
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

    except Exception:
        logger.exception(
            "Investigation failed for incident_id=%s",
            incident_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Investigation failed due to an internal server error.",
        ) from None


@app.post("/investigate/{incident_id}/summary")
def investigate_summary(incident_id: int, lang: str = "en"):
    language = _normalize_language(lang)

    try:
        engine = InvestigationEngine()
        result = engine.investigate(incident_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Incident {incident_id} not found",
            )

        decision = result.get("decision") or {}
        validation = result.get("decision_validation") or {}
        llm = result.get("llm_interpretation") or {}
        interpretation = llm.get("interpretation") or {}

        evidence = result.get("evidence") or {}
        detection = result.get("detection_evidence") or {}

        financial = evidence.get("financial") or {}
        customer = evidence.get("customer") or {}
        supplier = evidence.get("supplier") or {}

        scenario_metrics = {
            "demand": {
                "baseline_daily_orders": detection.get(
                    "baseline_daily_orders"
                ),
                "simulated_daily_orders": detection.get(
                    "simulated_daily_orders"
                ),
                "change_pct": detection.get("demand_change_pct"),
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
                "baseline_aov": financial.get("baseline_aov"),
                "current_aov": financial.get("current_aov"),
                "change_pct": financial.get("revenue_change_pct"),
            },
            "customer": {
                "baseline_review_score": customer.get(
                    "baseline_review_score"
                ),
                "current_review_score": customer.get(
                    "current_review_score"
                ),
                "change": customer.get("review_score_change"),
                "state": customer.get("customer_state"),
            },
            "supplier": {
                "baseline_risk": supplier.get("baseline_seller_risk"),
                "current_risk": supplier.get("current_seller_risk"),
                "pressure_change": supplier.get(
                    "supplier_pressure_change"
                ),
                "state": supplier.get("supplier_state"),
            },
        }

        summary = {
            "investigation_id": result.get("investigation_id"),
            "incident": result.get("incident"),
            "decision": {
                "status": decision.get("decision_status"),
                "recommended_action": decision.get("recommended_action"),
                "rationale": decision.get("rationale"),
            },
            "validation": {
                "status": validation.get("validation_status"),
            },
            "scenario_metrics": scenario_metrics,
            "root_cause_analysis": (
                result.get("root_cause_analysis") or {}
            ),
            "llm_interpretation": {
                "status": llm.get("interpretation_status"),
                "model": llm.get("model"),
                "executive_summary": interpretation.get(
                    "executive_summary"
                ),
                "key_observations": interpretation.get(
                    "key_observations"
                ) or [],
                "uncertainty": interpretation.get("uncertainty") or [],
                "unresolved_questions": interpretation.get(
                    "unresolved_questions"
                ) or [],
            },
            "provenance": result.get("provenance"),
            "language": "en",
        }

        if language != "en":
            summary = _translate_summary(summary, language)

        return summary

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Investigation summary failed for incident_id=%s",
            incident_id,
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Investigation summary failed due to an internal "
                "server error."
            ),
        ) from None


@app.get("/investigate/{incident_id}/summary")
def get_investigation_summary(incident_id: int, lang: str = "en"):
    return investigate_summary(incident_id, lang)
