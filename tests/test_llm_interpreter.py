from src.intelligence.llm_interpreter import LLMInterpreter


def test_llm_interpreter_result_contract():
    investigation = {
        "incident": {
            "incident_id": 1,
            "incident_type": "DEMAND_SUPPLY_IMBALANCE",
            "severity": "HIGH",
            "source_type": "SIMULATED",
        },
        "evidence": {
            "demand": {
                "change_pct": 25.0,
            },
            "inventory": {
                "cover_days": 9.18,
            },
        },
        "agent_analysis": {},
        "root_cause_analysis": {},
        "evidence_synthesis": {
            "causal_certainty": "NOT_ESTABLISHED",
        },
        "debate": {
            "status": (
                "CONSENSUS_WITH_UNRESOLVED_QUESTIONS"
            ),
        },
        "decision": {
            "status": "ACTIONABLE",
            "recommended_action": (
                "Prioritize inventory protection "
                "and monitor demand and supplier conditions."
            ),
        },
        "decision_validation": {
            "validation_status": "VALID",
        },
        "provenance": {
            "historical_data": "OBSERVED_HISTORICAL",
            "scenario_changes": "SIMULATED",
        },
    }

    interpreter = LLMInterpreter()
    result = interpreter.interpret(
        investigation
    )

    assert (
        result["interpretation_status"]
        == "INTERPRETATION_AVAILABLE"
    )

    assert result["model"]

    interpretation = result["interpretation"]

    expected_fields = {
        "executive_summary",
        "key_observations",
        "uncertainty",
        "unresolved_questions",
        "decision_explanation",
        "limitations",
    }

    assert set(interpretation.keys()) == expected_fields

    assert isinstance(
        interpretation["executive_summary"],
        str,
    )

    assert isinstance(
        interpretation["key_observations"],
        list,
    )

    assert isinstance(
        interpretation["uncertainty"],
        list,
    )

    assert isinstance(
        interpretation["unresolved_questions"],
        list,
    )

    assert isinstance(
        interpretation["decision_explanation"],
        str,
    )

    assert isinstance(
        interpretation["limitations"],
        list,
    )


def test_llm_interpreter_constraints():
    investigation = {
        "incident": {
            "incident_id": 1,
            "source_type": "SIMULATED",
        },
        "evidence": {},
        "agent_analysis": {},
        "root_cause_analysis": {},
        "evidence_synthesis": {},
        "debate": {},
        "decision": {
            "status": "ACTIONABLE",
            "recommended_action": "Monitor inventory.",
        },
        "decision_validation": {
            "validation_status": "VALID",
        },
        "provenance": {},
    }

    interpreter = LLMInterpreter()
    result = interpreter.interpret(
        investigation
    )

    constraints = result["constraints"]

    assert constraints["deterministic_business_facts"] is True
    assert constraints["llm_used"] is True
    assert constraints["business_facts_generated"] is False
    assert constraints["decision_modified"] is False
    assert constraints["rules_modified"] is False
    assert constraints["thresholds_modified"] is False
    assert constraints["causal_claims_generated"] is False