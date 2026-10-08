import json
import os

from dotenv import load_dotenv
from groq import Groq


class LLMInterpreter:
    """
    ORACLE-X LLM interpretation layer.

    Responsibilities:
    - Interpret deterministic investigation results.
    - Summarize evidence already produced by ORACLE-X.
    - Explain uncertainty and unresolved questions.
    - Explain the existing decision without modifying it.

    The interpreter must never:
    - invent business facts,
    - invent observed outcomes,
    - generate or modify business rules,
    - modify thresholds,
    - replace the deterministic decision,
    - assert an unproven causal root cause.
    """

    VERSION = "1.0"
    DEFAULT_MODEL = "openai/gpt-oss-120b"

    def __init__(
        self,
        api_key=None,
        model=DEFAULT_MODEL,
    ):
        load_dotenv()

        resolved_api_key = (
            api_key
            or os.getenv("GROQ_API_KEY")
        )

        if not resolved_api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=resolved_api_key
        )
        self.model = model

    def _build_prompt(self, investigation):
        payload = {
            "incident": investigation.get(
                "incident"
            ),
            "evidence": investigation.get(
                "evidence"
            ),
            "agent_analysis": investigation.get(
                "agent_analysis"
            ),
            "root_cause_analysis": investigation.get(
                "root_cause_analysis"
            ),
            "evidence_synthesis": investigation.get(
                "evidence_synthesis"
            ),
            "debate": investigation.get(
                "debate"
            ),
            "decision": investigation.get(
                "decision"
            ),
            "decision_validation": investigation.get(
                "decision_validation"
            ),
            "provenance": investigation.get(
                "provenance"
            ),
        }

        serialized_payload = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        return f"""
You are the interpretation layer of ORACLE-X.

Your role is strictly interpretive.

The deterministic ORACLE-X engine has already:
- detected the incident,
- collected evidence,
- analyzed agents,
- evaluated candidate root causes,
- synthesized evidence,
- debated the evidence,
- produced a decision,
- validated the decision.

You MUST NOT replace or modify any deterministic result.

You MUST NOT:
- invent facts,
- invent metrics,
- invent historical observations,
- invent outcomes,
- invent causal relationships,
- modify the decision,
- create a different recommendation,
- modify rules,
- modify thresholds,
- treat simulated data as historical observation.

You MAY:
- summarize the supplied evidence,
- explain the meaning of observed/model-derived/simulated evidence,
- explain uncertainty,
- explain why the existing decision follows from the supplied evidence,
- highlight limitations,
- restate unresolved questions.

Causal claims must remain explicitly unproven unless the supplied evidence already establishes them.

Every statement must be grounded in the supplied ORACLE-X payload.

Return ONLY valid JSON matching this schema:

{{
  "executive_summary": "string",
  "key_observations": [
    "string"
  ],
  "uncertainty": [
    "string"
  ],
  "unresolved_questions": [
    "string"
  ],
  "decision_explanation": "string",
  "limitations": [
    "string"
  ]
}}

ORACLE-X INVESTIGATION PAYLOAD:

{serialized_payload}
"""

    def _validate_result(
        self,
        result,
        investigation,
    ):
        required_fields = [
            "executive_summary",
            "key_observations",
            "uncertainty",
            "unresolved_questions",
            "decision_explanation",
            "limitations",
        ]

        if not isinstance(result, dict):
            raise ValueError(
                "LLM response must be a JSON object."
            )

        missing_fields = [
            field
            for field in required_fields
            if field not in result
        ]

        if missing_fields:
            raise ValueError(
                "LLM response is missing required "
                f"fields: {missing_fields}"
            )

        list_fields = [
            "key_observations",
            "uncertainty",
            "unresolved_questions",
            "limitations",
        ]

        for field in list_fields:
            if not isinstance(
                result[field],
                list,
            ):
                raise ValueError(
                    f"LLM field '{field}' "
                    "must be a list."
                )

        string_fields = [
            "executive_summary",
            "decision_explanation",
        ]

        for field in string_fields:
            if not isinstance(
                result[field],
                str,
            ):
                raise ValueError(
                    f"LLM field '{field}' "
                    "must be a string."
                )

        decision = investigation.get(
            "decision"
        )

        if decision:
            recommended_action = decision.get(
                "recommended_action"
            )

            if (
                recommended_action
                and recommended_action
                not in result[
                    "decision_explanation"
                ]
            ):
                result["decision_explanation"] = (
                    f"The deterministic decision "
                    f"was: {recommended_action}. "
                    f"{result['decision_explanation']}"
                )

        return result

    def interpret(
        self,
        investigation,
    ):
        if not isinstance(
            investigation,
            dict,
        ):
            raise ValueError(
                "Investigation must be a dictionary."
            )

        prompt = self._build_prompt(
            investigation
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the ORACLE-X "
                        "interpretation layer. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            max_tokens=1200,
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        if not content:
            raise ValueError(
                "LLM returned an empty response."
            )

        try:
            parsed_result = json.loads(
                content
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        validated_result = (
            self._validate_result(
                parsed_result,
                investigation,
            )
        )

        return {
            "interpretation_status": (
                "INTERPRETATION_AVAILABLE"
            ),
            "model": self.model,
            "interpretation": validated_result,
            "constraints": {
                "deterministic_business_facts": True,
                "llm_used": True,
                "business_facts_generated": False,
                "decision_modified": False,
                "rules_modified": False,
                "thresholds_modified": False,
                "causal_claims_generated": False,
            },
            "provenance": {
                "source": (
                    "DETERMINISTIC_INVESTIGATION_RESULTS"
                ),
                "interpretation_method": (
                    "LLM_EVIDENCE_INTERPRETATION"
                ),
                "model": self.model,
            },
            "version": self.VERSION,
        }