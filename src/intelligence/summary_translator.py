import copy
import os
import json
import re
from collections import Counter

from dotenv import load_dotenv


_NUMBER_PATTERN = re.compile(r"\d+(?:[.,]\d+)?")


class SummaryTranslator:
    """
    ORACLE-X presentation-language layer.

    Translates only the human-readable text fields of an investigation
    summary. Numbers, statuses, provenance labels, rules and decisions are
    never touched, so deterministic business logic stays authoritative.

    Safety net: a translated sentence is accepted only if it contains exactly
    the same numbers as the English original. Otherwise the original English
    sentence is kept.
    """

    VERSION = "1.0"
    DEFAULT_MODEL = "openai/gpt-oss-120b"
    LANGUAGES = {"ar": "Modern Standard Arabic"}
    BATCH_SIZE = 12

    # (language, english text) -> translated text, shared by all requests
    _cache = {}

    def __init__(self, api_key=None, model=DEFAULT_MODEL, client=None):
        self.model = model

        if client is not None:
            self.client = client
            return

        load_dotenv()

        resolved_api_key = api_key or os.getenv("GROQ_API_KEY")

        if not resolved_api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        from groq import Groq

        self.client = Groq(api_key=resolved_api_key)

    # ------------------------------------------------------------------
    # Low level translation
    # ------------------------------------------------------------------

    @staticmethod
    def _numbers(text):
        return Counter(_NUMBER_PATTERN.findall(text))

    def _request_batch(self, texts, language):
        language_name = self.LANGUAGES[language]

        system_prompt = (
            f"You translate business-analytics text from English to "
            f"{language_name}. Keep every number, percentage, currency amount "
            "and id exactly as written, using Western digits (0-9). Translate "
            "code identifiers such as HIGH_RISK, AT_RISK or ELEVATED_PRESSURE "
            "into natural words in the target language. Use clear, simple "
            "wording for non-technical readers. Preserve the original meaning "
            "exactly, including every statement of uncertainty. Do not add, "
            "remove or reinterpret any claim. The input is a JSON object that "
            "maps ids to English strings. Reply with ONLY a JSON object that "
            "maps the same ids to the translations. Translate every string. "
            "No markdown and no notes."
        )

        numbered = {str(i): text for i, text in enumerate(texts)}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(numbered, ensure_ascii=False),
                },
            ],
            temperature=0,
            max_tokens=8000,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Translation model returned an empty response.")

        start, end = content.find("{"), content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Translation model did not return JSON.")

        parsed = json.loads(content[start:end + 1])

        if not isinstance(parsed, dict):
            raise ValueError("Translation model returned a non-object.")

        return parsed

    def translate_texts(self, texts, language="ar"):
        """Return {english_text: translated_text} for every input text."""
        if language not in self.LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

        unique = []
        seen = set()

        for text in texts:
            if text not in seen:
                seen.add(text)
                unique.append(text)

        pending = [
            text for text in unique
            if (language, text) not in self._cache
        ]

        for offset in range(0, len(pending), self.BATCH_SIZE):
            batch = pending[offset:offset + self.BATCH_SIZE]
            parsed = self._request_batch(batch, language)

            for index, original in enumerate(batch):
                candidate = parsed.get(str(index))

                if not isinstance(candidate, str) or not candidate.strip():
                    continue

                candidate = candidate.strip()

                if self._numbers(candidate) != self._numbers(original):
                    continue

                self._cache[(language, original)] = candidate

        return {
            text: self._cache.get((language, text), text)
            for text in unique
        }

    # ------------------------------------------------------------------
    # Summary translation
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_references(summary):
        """(container, key) pairs for every translatable text field."""
        references = []

        def track(container, key):
            if not isinstance(container, (dict, list)):
                return

            try:
                value = container[key]
            except (KeyError, IndexError):
                return

            if isinstance(value, str) and value.strip():
                references.append((container, key))

        incident = summary.get("incident")
        for key in ("title", "summary"):
            track(incident, key)

        decision = summary.get("decision")
        for key in ("recommended_action", "rationale"):
            track(decision, key)

        llm = summary.get("llm_interpretation")

        if isinstance(llm, dict):
            track(llm, "executive_summary")

            for name in (
                "key_observations",
                "uncertainty",
                "unresolved_questions",
            ):
                items = llm.get(name)

                if isinstance(items, list):
                    for index in range(len(items)):
                        track(items, index)

        root_cause = summary.get("root_cause_analysis")

        if isinstance(root_cause, dict):
            for cause in root_cause.get("candidate_causes") or []:
                for key in (
                    "candidate_cause",
                    "evidence_for",
                    "evidence_against",
                ):
                    track(cause, key)

        return references

    def translate_summary(self, summary, language="ar"):
        """
        Return a copy of the summary with its text fields translated.

        Never raises for translation problems: on failure the English
        summary is returned with translation.status set to FAILED.
        """
        result = copy.deepcopy(summary)

        try:
            references = self._collect_references(result)
            originals = [
                container[key].strip()
                for container, key in references
            ]

            translations = self.translate_texts(originals, language)

            translated_count = 0

            for (container, key), original in zip(references, originals):
                translated = translations.get(original, original)

                if translated != original:
                    translated_count += 1

                container[key] = translated

            result["language"] = language
            result["translation"] = {
                "status": "OK",
                "language": language,
                "method": "LLM_TRANSLATION",
                "model": self.model,
                "fields_total": len(references),
                "fields_translated": translated_count,
                "numbers_verified": True,
            }

        except Exception as exc:
            result = copy.deepcopy(summary)
            result["language"] = "en"
            result["translation"] = {
                "status": "FAILED",
                "language": language,
                "reason": f"{type(exc).__name__}: {str(exc)[:160]}",
            }

        return result
