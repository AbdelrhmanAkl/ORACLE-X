import json
from types import SimpleNamespace

from src.intelligence.summary_translator import SummaryTranslator


class FakeClient:
    """Offline stand-in for the Groq client."""

    def __init__(self, mapping=None, fail=False):
        self.mapping = mapping or {}
        self.fail = fail
        self.calls = 0
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls += 1

        if self.fail:
            raise RuntimeError("boom")

        payload = json.loads(kwargs["messages"][1]["content"])
        reply = {
            key: self.mapping.get(text, f"AR:{text}")
            for key, text in payload.items()
        }

        message = SimpleNamespace(
            content=json.dumps(reply, ensure_ascii=False)
        )
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def make_summary():
    return {
        "incident": {
            "incident_id": 2,
            "title": "Demand and supply imbalance detected",
            "summary": "Simulated demand increased by 25.00%.",
            "severity": "HIGH",
        },
        "decision": {
            "status": "ACTIONABLE",
            "recommended_action": "Protect inventory.",
            "rationale": "Coverage declined.",
        },
        "scenario_metrics": {"demand": {"change_pct": 25.0}},
        "root_cause_analysis": {
            "candidate_causes": [
                {
                    "candidate_cause": "Demand Surge",
                    "evidence_for": "Orders rose 25%.",
                    "evidence_against": "Below the historical maximum.",
                    "confidence": "MODERATE",
                }
            ]
        },
        "llm_interpretation": {
            "status": "INTERPRETATION_AVAILABLE",
            "executive_summary": "Demand rose 25% in a simulation.",
            "key_observations": ["Orders rose from 270.64 to 338.30."],
            "uncertainty": [],
            "unresolved_questions": ["Is this unusual?"],
        },
        "provenance": {"scenario_changes": "SIMULATED"},
    }


def setup_function():
    SummaryTranslator._cache.clear()


def test_translates_text_but_never_touches_facts():
    translator = SummaryTranslator(client=FakeClient())
    original = make_summary()

    result = translator.translate_summary(original, "ar")

    assert result["incident"]["title"].startswith("AR:")
    assert result["decision"]["rationale"].startswith("AR:")
    assert result["llm_interpretation"]["key_observations"][0].startswith("AR:")

    # deterministic fields are untouched
    assert result["incident"]["severity"] == "HIGH"
    assert result["decision"]["status"] == "ACTIONABLE"
    assert result["scenario_metrics"] == original["scenario_metrics"]
    assert result["provenance"] == original["provenance"]
    assert result["root_cause_analysis"]["candidate_causes"][0]["confidence"] == "MODERATE"

    assert result["translation"]["status"] == "OK"
    assert result["language"] == "ar"

    # the input was not mutated
    assert original["incident"]["title"] == "Demand and supply imbalance detected"


def test_rejects_translation_that_changes_numbers():
    client = FakeClient(mapping={"Orders rose 25%.": "ارتفعت الطلبات 52%."})
    translator = SummaryTranslator(client=client)

    result = translator.translate_summary(make_summary(), "ar")

    cause = result["root_cause_analysis"]["candidate_causes"][0]
    assert cause["evidence_for"] == "Orders rose 25%."


def test_cache_avoids_second_model_call():
    client = FakeClient()
    translator = SummaryTranslator(client=client)

    translator.translate_summary(make_summary(), "ar")
    calls_after_first = client.calls
    translator.translate_summary(make_summary(), "ar")

    assert client.calls == calls_after_first


def test_failure_returns_english_summary():
    translator = SummaryTranslator(client=FakeClient(fail=True))
    original = make_summary()

    result = translator.translate_summary(original, "ar")

    assert result["translation"]["status"] == "FAILED"
    assert result["language"] == "en"
    assert result["incident"]["title"] == original["incident"]["title"]
