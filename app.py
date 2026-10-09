import html
import json
import os

import requests
import streamlit as st


API_URL = os.getenv(
    "ORACLE_X_API_URL",
    "https://oracle-x.fastapicloud.dev",
).rstrip("/")


st.set_page_config(
    page_title="ORACLE-X | Decision Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------

LANG_OPTIONS = {"English": "en", "العربية": "ar"}
LANG = LANG_OPTIONS.get(st.session_state.get("lang_choice", "English"), "en")
IS_AR = LANG == "ar"

STR = {
    "en": {
        "brand_tag": "Decision intelligence",
        "h1": "See what happened, why it happened, and what to do next.",
        "intro": "Pick a business incident and ORACLE-X will investigate it, check the evidence, and give you a clear recommendation you can verify.",
        "choose_incident": "Choose an incident",
        "incident_number": "Incident number",
        "incident_help": "Each incident is a detected business problem. Start with 2 to see an example.",
        "incident_item": "Incident {n}: {title}",
        "run": "Investigate this incident",
        "spinner": "Investigating. This can take up to a minute...",
        "err_timeout": "The request took too long. The investigation may still be running, so please try again in a moment.",
        "err_conn": "We couldn't reach the ORACLE-X service. Check your connection, or make sure the API is running.",
        "err_request": "The request failed: {e}",
        "err_404": "Incident #{n} doesn't exist. Try another number.",
        "err_http": "The service returned an error (HTTP {c}). Please try again.",
        "err_json": "The service sent back an unreadable response.",
        "err_missing": "The response is incomplete. Missing: {m}",
        "err_field": "The response is missing an expected field: {e}",
        "err_unexpected": "Something unexpected went wrong: {e}",
        "how_title": "How it works",
        "s1_t": "1. Choose an incident",
        "s1_d": "Pick a detected business problem. Incident 1 is a good place to start.",
        "s2_t": "2. We investigate",
        "s2_d": "Clear business rules look at demand, stock, revenue and customer reviews, then rank the likely causes.",
        "s3_t": "3. You get an answer",
        "s3_d": "A recommended action, the evidence behind it, and an honest list of what we're still unsure about.",
        "result": "Result",
        "result_sub": "Investigation finished for incident #{n}.",
        "incident": "Incident #{n}",
        "what_to_do": "What to do",
        "why": "Why:",
        "severity": "Severity: ",
        "decision": "Decision: ",
        "checks": "Checks: ",
        "data": "Data: ",
        "numbers": "The numbers",
        "numbers_sub": "A snapshot of the situation. Arrows show the change compared with normal.",
        "orders": "Orders per day",
        "stock": "Stock lasts",
        "days": "{v} days",
        "revenue": "Revenue per day",
        "reviews": "Review score",
        "scenario": "Scenario",
        "estimated": "Estimated",
        "metrics_note": "Orders, revenue and reviews come from a simulated scenario. Stock levels are estimated by a model, not counted in a warehouse.",
        "causes": "Likely causes",
        "causes_sub": "These are possible explanations, ranked by how well the evidence supports them. None of them is proven.",
        "supports": "What supports it",
        "holds_back": "What holds it back",
        "evidence": "Evidence: ",
        "confidence": "{v} confidence",
        "plain": "In plain words",
        "plain_note": "Written by an AI assistant to explain the findings. It cannot change the decision or the numbers.",
        "details": "Details",
        "details_sub": "Everything behind the recommendation, for anyone who wants to check.",
        "tab_seen": "What we found",
        "tab_unsure": "What we're unsure about",
        "tab_open": "Open questions",
        "tab_sources": "Where data comes from",
        "tab_tech": "Technical",
        "no_obs": "No observations were reported.",
        "no_unc": "No uncertainties were reported.",
        "no_q": "No open questions were reported.",
        "no_src": "No data sources were returned.",
        "src_note": "Each piece of information is labelled so you can tell real data from simulated, estimated or AI-written content.",
        "ai_status": "AI status",
        "ai_model": "AI model",
        "ai_perm": "AI permission",
        "read_only": "Read only",
        "rule_based": "Rule-based analysis",
        "claims_cert": "Claims a certain cause",
        "hist_used": "Historical data used",
        "tech_callout": "The AI only explains results that were already produced. Business rules decide the facts, the recommendation and its verification.",
        "footer": "Decisions are produced and verified by fixed business rules. Simulated inputs are always labelled, estimated values stay traceable, and the cause analysis never claims more certainty than the evidence allows. The AI assistant only explains the results.",
        "ar_note": "",
        "translating": "Translating...",
        "tr_note": "",
    },
    "ar": {
        "brand_tag": "ذكاء القرارات",
        "h1": "اعرف ماذا حدث، ولماذا حدث، وماذا تفعل بعد ذلك.",
        "intro": "اختر حادثة من حوادث العمل، وسيقوم ORACLE-X بالتحقيق فيها وفحص الأدلة وتقديم توصية واضحة يمكنك التحقق منها.",
        "choose_incident": "اختر الحادثة",
        "incident_number": "رقم الحادثة",
        "incident_help": "كل حادثة هي مشكلة عمل تم رصدها. ابدأ بالرقم 2 لمشاهدة مثال.",
        "incident_item": "حادثة {n}: {title}",
        "run": "ابدأ التحقيق",
        "spinner": "جارٍ التحقيق، وقد يستغرق ذلك حتى دقيقة...",
        "err_timeout": "استغرق الطلب وقتًا طويلًا. قد يكون التحقيق ما زال جاريًا، حاول مرة أخرى بعد قليل.",
        "err_conn": "تعذّر الوصول إلى خدمة ORACLE-X. تأكد من اتصالك بالإنترنت أو من أن الخدمة تعمل.",
        "err_request": "فشل الطلب: {e}",
        "err_404": "الحادثة رقم {n} غير موجودة. جرّب رقمًا آخر.",
        "err_http": "أعادت الخدمة خطأ (HTTP {c}). حاول مرة أخرى.",
        "err_json": "أرسلت الخدمة ردًا غير مقروء.",
        "err_missing": "الرد غير مكتمل. الأجزاء الناقصة: {m}",
        "err_field": "الرد ينقصه حقل متوقع: {e}",
        "err_unexpected": "حدث خطأ غير متوقع: {e}",
        "how_title": "كيف يعمل؟",
        "s1_t": "1. اختر حادثة",
        "s1_d": "اختر مشكلة عمل تم رصدها. الحادثة رقم 1 بداية جيدة.",
        "s2_t": "2. نقوم بالتحقيق",
        "s2_d": "قواعد عمل واضحة تفحص الطلب والمخزون والإيرادات وتقييمات العملاء، ثم ترتب الأسباب المحتملة.",
        "s3_t": "3. تحصل على إجابة",
        "s3_d": "إجراء موصى به، والأدلة التي تدعمه، وقائمة صريحة بما لا نزال غير متأكدين منه.",
        "result": "النتيجة",
        "result_sub": "انتهى التحقيق في الحادثة رقم {n}.",
        "incident": "حادثة رقم {n}",
        "what_to_do": "ماذا تفعل",
        "why": "السبب:",
        "severity": "الخطورة: ",
        "decision": "القرار: ",
        "checks": "الفحوصات: ",
        "data": "البيانات: ",
        "numbers": "الأرقام",
        "numbers_sub": "لمحة عن الوضع الحالي. تُظهر الأسهم التغيّر مقارنةً بالوضع المعتاد.",
        "orders": "الطلبات يوميًا",
        "stock": "مدة كفاية المخزون",
        "days": "{v} يوم",
        "revenue": "الإيراد اليومي",
        "reviews": "تقييم العملاء",
        "scenario": "سيناريو",
        "estimated": "تقديري",
        "metrics_note": "الطلبات والإيرادات والتقييمات مصدرها سيناريو محاكاة. أما المخزون فتقدّره الأنظمة بنموذج حسابي، ولم يُجرد في مستودع حقيقي.",
        "causes": "الأسباب المحتملة",
        "causes_sub": "هذه تفسيرات محتملة مرتبة حسب قوة الأدلة التي تدعمها. ولم يثبت أي منها.",
        "supports": "ما يدعمه",
        "holds_back": "ما يضعف الثقة فيه",
        "evidence": "نوع الدليل: ",
        "confidence": "ثقة {v}",
        "plain": "بكلمات بسيطة",
        "plain_note": "كتبه مساعد ذكاء اصطناعي لشرح النتائج، ولا يمكنه تغيير القرار أو الأرقام.",
        "details": "التفاصيل",
        "details_sub": "كل ما يقف خلف التوصية، لمن يريد التحقق.",
        "tab_seen": "ما وجدناه",
        "tab_unsure": "ما لسنا متأكدين منه",
        "tab_open": "أسئلة مفتوحة",
        "tab_sources": "مصدر البيانات",
        "tab_tech": "تفاصيل تقنية",
        "no_obs": "لا توجد ملاحظات.",
        "no_unc": "لا توجد نقاط عدم يقين.",
        "no_q": "لا توجد أسئلة مفتوحة.",
        "no_src": "لم تُرجع الخدمة أي مصادر بيانات.",
        "src_note": "كل معلومة موسومة حتى تعرف إن كانت بيانات حقيقية أو محاكاة أو تقديرًا أو شرحًا كتبه الذكاء الاصطناعي.",
        "ai_status": "حالة الذكاء الاصطناعي",
        "ai_model": "النموذج",
        "ai_perm": "صلاحية الذكاء الاصطناعي",
        "read_only": "قراءة فقط",
        "rule_based": "تحليل قائم على قواعد",
        "claims_cert": "يدّعي سببًا مؤكدًا",
        "hist_used": "استخدام بيانات تاريخية",
        "tech_callout": "الذكاء الاصطناعي يشرح فقط نتائج تم إنتاجها مسبقًا. أما الحقائق والتوصية والتحقق منها فتحددها قواعد العمل.",
        "footer": "القرارات تنتجها وتتحقق منها قواعد عمل ثابتة. المدخلات المحاكاة موسومة دائمًا، والقيم التقديرية قابلة للتتبع، وتحليل الأسباب لا يدّعي يقينًا أكثر مما تسمح به الأدلة. ويقتصر دور الذكاء الاصطناعي على شرح النتائج.",
        "ar_note": "بعض النصوص التفصيلية القادمة من الخادم قد تظهر بالإنجليزية لأن الترجمة التلقائية غير مفعّلة.",
        "translating": "جارٍ الترجمة...",
        "tr_note": "تمت ترجمة نصوص النتائج تلقائيًا بالذكاء الاصطناعي، وقد تحتوي على فروق بسيطة عن الأصل الإنجليزي.",
    },
}

# The seven incidents: id -> (English name, Arabic name)
INCIDENT_NAMES = {
    1: ("Demand & Supply Imbalance", "اختلال الطلب والعرض"),
    2: ("Revenue Decline", "انخفاض الإيرادات"),
    3: ("Inventory Shortage", "نقص المخزون"),
    4: ("Customer Satisfaction Drop", "تراجع رضا العملاء"),
    5: ("Delivery Performance Issue", "مشكلة أداء التوصيل"),
    6: ("Seller Performance Risk", "مخاطر أداء البائعين"),
    7: ("Operational Cost Increase", "ارتفاع التكاليف التشغيلية"),
}

# Users see incidents numbered 1 to 7. The backend stores them as 2 to 8.
API_ID_OFFSET = 1


def t(key, **kw):
    text = STR[LANG][key]
    return text.format(**kw) if kw else text


PRETTY = {
    "en": {
        "ACTIONABLE": "Action recommended",
        "VALID": "Verified",
        "INVALID": "Failed verification",
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
        "CRITICAL": "Critical",
        "MODERATE": "Moderate",
        "SIMULATED": "Simulated",
        "TRUE": "Yes",
        "FALSE": "No",
        "INTERPRETATION_AVAILABLE": "Available",
        "OBSERVED_HISTORICAL": "Real historical data",
        "MODEL_DERIVED": "Calculated by a model",
        "DETERMINISTIC_RCA": "Rule-based analysis",
        "DETERMINISTIC_OBSERVED_OUTCOMES": "Rule-based, from real outcomes",
        "DETERMINISTIC_READ_ONLY": "Rule-based, read only",
        "LLM_EVIDENCE_INTERPRETATION": "AI-written explanation",
    },
    "ar": {
        "ACTIONABLE": "يوصى باتخاذ إجراء",
        "VALID": "تم التحقق",
        "INVALID": "فشل التحقق",
        "HIGH": "مرتفعة",
        "MEDIUM": "متوسطة",
        "LOW": "منخفضة",
        "CRITICAL": "حرجة",
        "MODERATE": "متوسطة",
        "SIMULATED": "محاكاة",
        "TRUE": "نعم",
        "FALSE": "لا",
        "INTERPRETATION_AVAILABLE": "متاح",
        "OBSERVED_HISTORICAL": "بيانات تاريخية حقيقية",
        "MODEL_DERIVED": "محسوبة بنموذج",
        "DETERMINISTIC_RCA": "تحليل قائم على قواعد",
        "DETERMINISTIC_OBSERVED_OUTCOMES": "قائم على قواعد ومن نتائج فعلية",
        "DETERMINISTIC_READ_ONLY": "قائم على قواعد (قراءة فقط)",
        "LLM_EVIDENCE_INTERPRETATION": "شرح كتبه الذكاء الاصطناعي",
        "SIMULATED_WITH_HISTORICAL_CONTEXT": "محاكاة مع سياق تاريخي",
        "SIMULATED_MODEL_DERIVED": "محاكاة ومحسوبة بنموذج",
        "SIMULATED_DOWNSTREAM_IMPACT": "أثر لاحق ضمن المحاكاة",
        "HISTORICAL_DATA": "البيانات التاريخية",
        "INVENTORY_LEVEL_AND_COVERAGE": "مستوى المخزون ومدته",
        "SCENARIO_CHANGES": "تغييرات السيناريو",
        "ROOT_CAUSE_INTERPRETATION": "تفسير الأسباب",
        "LEARNING": "التعلّم",
        "ADAPTIVE_INTELLIGENCE": "الذكاء التكيفي",
        "LLM_USED": "استخدام الذكاء الاصطناعي",
        "LLM_INTERPRETATION": "شرح الذكاء الاصطناعي",
        "INSUFFICIENT_EVIDENCE": "أدلة غير كافية",
        "INSUFFICIENT-EVIDENCE": "أدلة غير كافية",
        "INSUFFICIENT_LEARNING_DATA": "بيانات تعلّم غير كافية",
        "PENDING": "قيد الانتظار",
        "COMPLETED": "مكتمل",
        "FAILED": "فشل",
        "REJECTED": "مرفوض",
        "WARNING": "تحذير",
        "PASS": "ناجح",
        "ERROR": "خطأ",
        "AVAILABLE": "متاح",
        "STRUCTURALLY_STRONG": "قوي هيكليًا",
        "N/A": "غير متاح",
    },
}

# Server texts that are fixed sentences can be shown in Arabic.
# Anything not listed here (for example sentences with live numbers
# or the AI-written summary) is shown as it arrives from the API.
DYN_AR = {
    "Demand and supply imbalance detected": "رُصد عدم توازن بين الطلب والإمداد",
    "Simulated demand increased while inventory coverage declined below the configured safety threshold.": "ارتفع الطلب المحاكى بينما انخفضت مدة تغطية المخزون إلى ما دون حد الأمان المحدد.",
    "Prioritize inventory protection and monitor demand and supplier conditions.": "أعطِ الأولوية لحماية المخزون، وراقب الطلب وأوضاع الموردين.",
    "Simulated inventory coverage declined materially while simulated business activity increased. The evidence supports a protective operational response, but does not establish a single causal root cause.": "انخفضت مدة تغطية المخزون المحاكاة بشكل ملحوظ بينما زاد النشاط التجاري المحاكى. تدعم الأدلة اتخاذ إجراء وقائي، لكنها لا تثبت سببًا جذريًا واحدًا.",
    "Demand Surge": "ارتفاع الطلب",
    "Inventory Pressure": "ضغط على المخزون",
    "Supplier Pressure": "ضغط على الموردين",
    "Customer Experience Deterioration": "تراجع تجربة العملاء",
    "Supplier pressure is a controlled simulated condition, not an observed historical causal relationship.": "ضغط الموردين حالة محاكاة مضبوطة، وليس علاقة سببية ثبتت من البيانات التاريخية.",
    "Customer deterioration is downstream simulated evidence and does not establish causal origin.": "تراجع تجربة العملاء دليل لاحق ضمن المحاكاة ولا يثبت أصل السبب.",
    "Inventory level and coverage are model-derived because the source dataset does not contain actual stock levels.": "مستوى المخزون ومدته محسوبان بنموذج لأن البيانات الأصلية لا تحتوي على مستويات المخزون الفعلية.",
    "All evidence originates from a simulated scenario; real-world validation is absent.": "كل الأدلة مصدرها سيناريو محاكاة، ولا يوجد تحقق من الواقع.",
    "Inventory levels and coverage are model-derived, not observed stock counts.": "مستويات المخزون ومدتها محسوبة بنموذج وليست جردًا فعليًا.",
    "Demand increase, while sizable, remains below the historical maximum, limiting certainty that it is an outlier event.": "زيادة الطلب كبيرة لكنها أقل من أعلى مستوى تاريخي، مما يقلل اليقين بأنها حدث استثنائي.",
    "Supplier pressure is a controlled simulation variable, not an empirically observed driver.": "ضغط الموردين متغير محاكاة مضبوط وليس عاملًا ثبت بالملاحظة.",
    "Downstream customer experience decline cannot be linked causally to upstream factors without additional data.": "لا يمكن ربط تراجع تجربة العملاء بالعوامل السابقة له سببيًا دون بيانات إضافية.",
    "Does the simulated demand increase represent a historically unusual demand event?": "هل تمثل زيادة الطلب المحاكاة حدثًا غير معتاد تاريخيًا؟",
    "Is inventory pressure an initiating factor or a consequence of the simulated demand increase?": "هل الضغط على المخزون سبب بادئ أم نتيجة لزيادة الطلب المحاكاة؟",
    "Does supplier pressure represent an observed operational relationship or only a controlled simulation condition?": "هل يمثل ضغط الموردين علاقة تشغيلية فعلية أم مجرد حالة محاكاة مضبوطة؟",
    "Can the simulated customer deterioration be attributed to the demand and inventory conditions without additional historical evidence?": "هل يمكن ربط تراجع تجربة العملاء المحاكى بحالة الطلب والمخزون دون أدلة تاريخية إضافية؟",
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def esc(value):
    """Escape any API-provided value before putting it inside HTML."""
    if value is None:
        return ""
    return html.escape(str(value))


RUNTIME_TR = {}  # filled per run with automatic Arabic translations


def dyn(value):
    """Return the Arabic version of a server text when one is available."""
    if IS_AR and isinstance(value, str):
        key = value.strip()
        return DYN_AR.get(key) or RUNTIME_TR.get(key) or value
    return value


GROQ_MODEL = os.getenv("ORACLE_X_TRANSLATE_MODEL", "openai/gpt-oss-120b")


def get_groq_key():
    """Read the Groq key from Streamlit secrets or the environment."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        key = None
    return key or os.getenv("GROQ_API_KEY")


@st.cache_data(ttl=86400, show_spinner=False)
def translate_to_arabic(texts):
    """
    Translate a tuple of English texts to Arabic with Groq.
    Returns {english: arabic}. Raises on failure so failures are not cached.
    """
    key = get_groq_key()
    if not key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    system = (
        "You translate business-analytics text from English to Modern Standard "
        "Arabic. Keep every number, percentage, currency amount and incident id "
        "exactly as written. Translate code identifiers such as HIGH_RISK, "
        "AT_RISK or ELEVATED_PRESSURE into natural Arabic words as well. "
        "Use clear, simple wording for non-technical readers and keep the "
        "original meaning, including every statement of uncertainty. "
        "The input is a JSON object that maps ids to English strings. Reply "
        "with ONLY a JSON object with the same ids mapped to the Arabic "
        "translations. Translate every single string. No markdown, no notes."
    )
    numbered = {str(i): text for i, text in enumerate(texts)}
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": GROQ_MODEL,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(numbered, ensure_ascii=False)},
            ],
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    start, end = content.find("{"), content.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("translation reply was not JSON")
    translated = json.loads(content[start:end + 1])

    result = {}
    for i, text in enumerate(texts):
        value = translated.get(str(i))
        if isinstance(value, str) and value.strip():
            result[text] = value.strip()
    if not result:
        raise ValueError("translation reply was empty")
    return result


def collect_server_texts(payload):
    """Every free-text string from the API that the page shows."""
    found = []

    def add(value):
        if isinstance(value, str) and value.strip():
            found.append(value.strip())

    incident = payload.get("incident", {}) or {}
    decision = payload.get("decision", {}) or {}
    llm = payload.get("llm_interpretation", {}) or {}
    rca = payload.get("root_cause_analysis", {}) or {}

    for value in (
        incident.get("title"),
        incident.get("summary"),
        decision.get("recommended_action"),
        decision.get("rationale"),
        llm.get("executive_summary"),
    ):
        add(value)

    for name in ("key_observations", "uncertainty", "unresolved_questions"):
        for value in llm.get(name, []) or []:
            add(value)

    for cause in rca.get("candidate_causes", []) or []:
        for name in ("candidate_cause", "evidence_for", "evidence_against"):
            add(cause.get(name))

    # unique, keep order, skip what is already translated by hand
    seen, todo = set(), []
    for text in found:
        if text not in seen and text not in DYN_AR:
            seen.add(text)
            todo.append(text)
    return todo


def bidi(value):
    """Escape text and isolate its direction (fixes stray punctuation in RTL)."""
    return f"<bdi>{esc(value)}</bdi>"


def md(markup):
    """
    Render an HTML snippet.

    Lines are stripped (so Streamlit never treats indented HTML as a code
    block) and joined with a space (so words on separate lines never glue
    together).
    """
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    if IS_AR:
        flat = f'<div dir="rtl" style="text-align:right">{flat}</div>'
    st.markdown(flat, unsafe_allow_html=True)


def pretty(value):
    """Turn API codes like INSUFFICIENT_EVIDENCE into readable text."""
    text = str(value).strip()
    key = text.upper()
    if key in PRETTY[LANG]:
        return PRETTY[LANG][key]
    if key in PRETTY["en"] and not IS_AR:
        return PRETTY["en"][key]
    return text.replace("_", " ").capitalize()


def tone_for(value):
    v = str(value).strip().upper()
    if v in {"VALID", "PASS", "COMPLETED", "TRUE", "AVAILABLE",
             "STRUCTURALLY_STRONG", "LOW", "OBSERVED_HISTORICAL",
             "INTERPRETATION_AVAILABLE"}:
        return "good"
    if v in {"ACTIONABLE", "MODEL_DERIVED"}:
        return "info"
    if v in {"MEDIUM", "MODERATE", "WARNING", "PENDING", "SIMULATED",
             "INSUFFICIENT_LEARNING_DATA", "INSUFFICIENT-EVIDENCE"}:
        return "warn"
    if v in {"HIGH", "CRITICAL", "INVALID", "FAILED", "REJECTED",
             "FALSE", "ERROR"}:
        return "bad"
    return "neutral"


def chip(text, tone="neutral", prefix=""):
    label = f"<span class='ox-chip-prefix'>{esc(prefix)}</span>" if prefix else ""
    return f"<span class='ox-chip ox-{tone}'><i></i>{label}{esc(text)}</span>"


def num(source, key, default=0.0):
    try:
        return float(source.get(key, default))
    except (TypeError, ValueError, AttributeError):
        return default


def items_html(items, empty_text):
    if not items:
        return f"<div class='ox-empty-line'>{esc(empty_text)}</div>"
    rows = "".join(f"<li>{bidi(dyn(i))}</li>" for i in items)
    return f"<ul class='ox-list'>{rows}</ul>"


def metric_card(label, value, delta_text, delta_value, source_text, source_tone):
    if delta_value > 0:
        d_tone, arrow = "good", "▲"
    elif delta_value < 0:
        d_tone, arrow = "bad", "▼"
    else:
        d_tone, arrow = "neutral", "–"
    return f"""
    <div class="ox-metric">
        <div class="ox-metric-label">{esc(label)}</div>
        <div class="ox-metric-value">{esc(value)}</div>
        <div class="ox-metric-foot">
            <span class="ox-delta ox-{d_tone}">{arrow} {esc(delta_text)}</span>
            {chip(source_text, source_tone)}
        </div>
    </div>
    """


def confidence_meter(level):
    v = str(level).strip().upper()
    filled = {"LOW": 1, "MEDIUM": 2, "MODERATE": 2, "HIGH": 3}.get(v, 0)
    tone = {1: "bad", 2: "warn", 3: "good"}.get(filled, "neutral")
    bars = "".join(
        f"<b class='{'ox-on ox-' + tone if i < filled else ''}'></b>"
        for i in range(3)
    )
    return f"""
    <div class="ox-confidence">
        <div class="ox-meter">{bars}</div>
        <span>{esc(t("confidence", v=pretty(level)))}</span>
    </div>
    """


def section(title, subtitle=""):
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    md(f"<div class='ox-section'><h3>{esc(title)}</h3>{sub}</div>")


# ---------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #12141c;
    --ink-2: #454a58;
    --muted: #7a8090;
    --line: #e8eaf0;
    --line-2: #d9dce5;
    --bg: #ffffff;
    --soft: #f6f7fa;
    --accent: #3555f0;
    --accent-soft: #eef1ff;
    --good: #12805c;   --good-bg: #e8f6f0;
    --warn: #a8620a;   --warn-bg: #fdf3e2;
    --bad: #c23b3b;    --bad-bg: #fdecec;
    --info: #3555f0;   --info-bg: #eef1ff;
    --neutral: #5b6070; --neutral-bg: #f1f2f6;
    --r-sm: 10px;
    --r-lg: 20px;
}

html, body, .stApp, .stMarkdown, button, input, textarea,
[data-baseweb="tab"], [data-baseweb="select"], [data-testid="stNumberInput"] {
    font-family: 'Plus Jakarta Sans', 'Cairo', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.stApp { background: var(--bg); color: var(--ink); }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1080px; padding: 2.2rem 1.6rem 5rem 1.6rem; }
[data-testid="stVerticalBlock"] { gap: 0.9rem; }

.ox-top { display: flex; align-items: center; gap: 0.7rem; padding-bottom: 0.4rem; }
.ox-logo {
    width: 38px; height: 38px; border-radius: 11px;
    background: var(--ink); color: #fff;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}
.ox-brand-name { font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; color: var(--ink); }
.ox-brand-tag { font-size: 0.78rem; color: var(--muted); margin-top: 1px; }

/* language switch */
[data-testid="stRadio"] [role="radiogroup"] {
    gap: 0.3rem; background: var(--soft); border: 1px solid var(--line);
    border-radius: 999px; padding: 0.2rem; width: fit-content;
}
[data-testid="stRadio"] label { padding: 0.25rem 0.8rem; border-radius: 999px; margin: 0; }
[data-testid="stRadio"] label p { font-size: 0.82rem; font-weight: 600; color: var(--ink-2); }
[data-testid="stRadio"] label:has(input:checked) { background: #fff; box-shadow: 0 1px 3px rgba(18,20,28,0.12); }
[data-testid="stRadio"] label:has(input:checked) p { color: var(--ink); }
[data-testid="stRadio"] label > div:first-child { display: none; }

.ox-intro { padding: 1.4rem 0 0.4rem 0; }
.ox-intro h1 {
    font-size: 2.7rem; line-height: 1.15; font-weight: 800;
    letter-spacing: -0.03em; color: var(--ink); margin: 0; padding: 0;
}
.ox-intro p { max-width: 640px; margin: 0.9rem 0 0 0; font-size: 1.02rem; line-height: 1.7; color: var(--ink-2); }

[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--line) !important;
    border-radius: var(--r-lg) !important;
    background: var(--soft);
    padding: 0.4rem 0.5rem;
}
[data-testid="stNumberInput"] label p, [data-testid="stSelectbox"] label p {
    font-size: 0.85rem; font-weight: 600; color: var(--ink);
}
[data-testid="stNumberInput"] input { background: #fff; color: var(--ink); font-weight: 600; border-radius: var(--r-sm); }
[data-testid="stNumberInput"] div[data-baseweb="input"] { border-radius: var(--r-sm); border: 1px solid var(--line-2); background: #fff; }
[data-testid="stNumberInput"] button { background: #fff; color: var(--ink-2); }
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #fff; border-radius: var(--r-sm); border: 1px solid var(--line-2); min-height: 44px; font-weight: 600;
}
.stButton > button {
    min-height: 46px; border-radius: var(--r-sm);
    background: var(--accent); border: 1px solid var(--accent);
    color: #fff; font-weight: 700; font-size: 0.95rem; transition: background 0.15s ease;
}
.stButton > button p { color: #fff !important; font-weight: 700; }
.stButton > button:hover { background: #2a45d1; border-color: #2a45d1; color: #fff; }
.stButton > button:focus-visible { outline: 3px solid #b9c5ff; outline-offset: 2px; }

.ox-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin-top: 0.4rem; }
.ox-step { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.2rem 1.3rem; }
.ox-step b { display: block; font-size: 0.98rem; color: var(--ink); margin-bottom: 0.3rem; }
.ox-step span { font-size: 0.88rem; line-height: 1.6; color: var(--ink-2); }

.ox-section { margin: 1.9rem 0 0.2rem 0; }
.ox-section h3 { font-size: 1.35rem; font-weight: 750; letter-spacing: -0.02em; color: var(--ink); margin: 0; padding: 0; }
.ox-section p { margin: 0.35rem 0 0 0; font-size: 0.92rem; line-height: 1.6; color: var(--muted); max-width: 680px; }

.ox-chip {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.65rem; border-radius: 999px;
    font-size: 0.78rem; font-weight: 650; white-space: nowrap;
}
.ox-chip i { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.ox-chip-prefix { font-weight: 500; opacity: 0.75; margin-inline-end: -0.2rem; }
.ox-chip.ox-good, .ox-delta.ox-good { background: var(--good-bg); color: var(--good); }
.ox-chip.ox-warn, .ox-delta.ox-warn { background: var(--warn-bg); color: var(--warn); }
.ox-chip.ox-bad,  .ox-delta.ox-bad  { background: var(--bad-bg);  color: var(--bad); }
.ox-chip.ox-info, .ox-delta.ox-info { background: var(--info-bg); color: var(--info); }
.ox-chip.ox-neutral, .ox-delta.ox-neutral { background: var(--neutral-bg); color: var(--neutral); }

.ox-verdict {
    border: 1px solid var(--line); border-radius: 24px; padding: 2rem 2.1rem; background: #fff;
    box-shadow: 0 1px 0 rgba(18, 20, 28, 0.02), 0 18px 40px -24px rgba(18, 20, 28, 0.18);
}
.ox-incident-id { font-size: 0.85rem; font-weight: 600; color: var(--muted); }
.ox-verdict-title { font-size: 1.9rem; line-height: 1.25; font-weight: 800; letter-spacing: -0.03em; color: var(--ink); margin: 0.5rem 0 0 0; }
.ox-verdict-sub { font-size: 1rem; line-height: 1.7; color: var(--ink-2); margin: 0.7rem 0 0 0; max-width: 720px; }
.ox-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.3rem; }

.ox-action { margin-top: 1.4rem; padding: 1.4rem 1.6rem; border-radius: var(--r-lg); background: var(--accent-soft); }
.ox-action-label { font-size: 0.85rem; font-weight: 700; color: var(--accent); }
.ox-action-text { font-size: 1.3rem; line-height: 1.5; font-weight: 700; color: var(--ink); margin-top: 0.35rem; }
.ox-action-why { font-size: 0.92rem; line-height: 1.7; color: var(--ink-2); margin-top: 0.7rem; }

.ox-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.9rem; }
.ox-metric { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.2rem 1.25rem; background: #fff; }
.ox-metric-label { font-size: 0.88rem; font-weight: 600; color: var(--ink-2); }
.ox-metric-value { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.03em; color: var(--ink); margin-top: 0.5rem; }
.ox-metric-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 0.45rem; margin-top: 0.8rem; }
.ox-delta { display: inline-flex; padding: 0.3rem 0.6rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; direction: ltr; unicode-bidi: isolate; }
.ox-note { font-size: 0.82rem; color: var(--muted); margin-top: 0.7rem; line-height: 1.6; }

.ox-causes { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.9rem; }
.ox-cause { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.3rem 1.4rem; background: #fff; }
.ox-cause-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.ox-cause-title { font-size: 1.05rem; font-weight: 750; color: var(--ink); }
.ox-confidence { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; font-size: 0.75rem; color: var(--muted); font-weight: 600; white-space: nowrap; }
.ox-meter { display: flex; gap: 3px; }
.ox-meter b { width: 20px; height: 6px; border-radius: 3px; background: var(--line); display: block; }
.ox-meter b.ox-on.ox-good { background: var(--good); }
.ox-meter b.ox-on.ox-warn { background: #e0a23b; }
.ox-meter b.ox-on.ox-bad  { background: var(--bad); }
.ox-cause-block { margin-top: 1rem; }
.ox-cause-block b { display: block; font-size: 0.8rem; font-weight: 700; color: var(--ink); margin-bottom: 0.2rem; }
.ox-cause-block span { font-size: 0.88rem; line-height: 1.6; color: var(--ink-2); }
.ox-cause-type { margin-top: 1rem; }

.ox-plain { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.5rem 1.7rem; background: var(--soft); }
.ox-plain p { font-size: 1.02rem; line-height: 1.85; color: var(--ink); margin: 0; }
.ox-plain small { display: block; margin-top: 1rem; font-size: 0.8rem; color: var(--muted); }

[data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--line); }
[data-baseweb="tab"] { height: 44px; padding: 0 0.9rem; font-weight: 600; color: var(--muted); background: transparent; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--ink); }
[data-baseweb="tab-highlight"] { background: var(--ink); height: 2px; }
[data-baseweb="tab-border"] { display: none; }

.ox-list { margin: 0.6rem 0 0 0; padding: 0; list-style: none; }
.ox-list li {
    position: relative; padding: 0.7rem 0 0.7rem 1.4rem; border-bottom: 1px solid var(--line);
    font-size: 0.95rem; line-height: 1.7; color: var(--ink-2);
}
.ox-list li:last-child { border-bottom: none; }
.ox-list li::before { content: ""; position: absolute; left: 0.2rem; top: 1.3rem; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
.ox-empty-line { padding: 1rem 0; font-size: 0.92rem; color: var(--muted); }

.ox-sources { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.7rem; margin-top: 0.8rem; }
.ox-source { display: flex; align-items: center; justify-content: space-between; gap: 1rem; border: 1px solid var(--line); border-radius: var(--r-sm); padding: 0.8rem 1rem; }
.ox-source span { font-size: 0.9rem; font-weight: 600; color: var(--ink); }

.ox-tech { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin-top: 0.8rem; }
.ox-tech div { border: 1px solid var(--line); border-radius: var(--r-sm); padding: 0.9rem 1rem; }
.ox-tech small { display: block; font-size: 0.78rem; color: var(--muted); font-weight: 600; }
.ox-tech b { display: block; font-size: 0.95rem; color: var(--ink); margin-top: 0.25rem; word-break: break-word; }
.ox-callout { margin-top: 0.9rem; padding: 1rem 1.2rem; border-radius: var(--r-sm); background: var(--accent-soft); color: var(--ink-2); font-size: 0.9rem; line-height: 1.7; }

.ox-footer { margin-top: 2.5rem; padding-top: 1.4rem; border-top: 1px solid var(--line); font-size: 0.82rem; line-height: 1.75; color: var(--muted); max-width: 760px; }

[data-testid="stAlert"] { border-radius: var(--r-sm); }

@media (max-width: 900px) {
    .block-container { padding: 1.2rem 1rem 4rem 1rem; }
    .ox-intro h1 { font-size: 2rem; }
    .ox-metrics { grid-template-columns: repeat(2, 1fr); }
    .ox-causes, .ox-sources, .ox-tech, .ox-steps { grid-template-columns: 1fr; }
    .ox-verdict { padding: 1.4rem 1.3rem; }
    .ox-verdict-title { font-size: 1.5rem; }
}
@media (max-width: 520px) {
    .ox-metrics { grid-template-columns: 1fr; }
}
</style>
    """,
    unsafe_allow_html=True,
)

if IS_AR:
    st.markdown(
        """
<style>
html, body, .stApp, .stMarkdown, button, input, textarea,
[data-baseweb="tab"], [data-baseweb="select"], [data-testid="stNumberInput"] {
    font-family: 'Cairo', 'Plus Jakarta Sans', system-ui, sans-serif;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.block-container, [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
[data-testid="stMarkdownContainer"], [data-testid="stAlert"], [data-testid="stSpinner"],
[data-testid="stTabs"], [data-baseweb="tab-list"], [data-testid="stSelectbox"],
[data-testid="stNumberInput"], [data-testid="stRadio"], .stButton {
    direction: rtl !important;
    text-align: right !important;
}
[data-testid="stMarkdownContainer"] p { text-align: right !important; }
[data-testid="stNumberInput"] input { direction: ltr !important; text-align: left !important; }
[data-testid="stSelectbox"] div[data-baseweb="select"] * { text-align: right !important; direction: rtl !important; }
[data-baseweb="popover"] li, [data-baseweb="popover"] ul { direction: rtl !important; text-align: right !important; }
[data-testid="stRadio"] [role="radiogroup"] { margin-inline-start: 0; }
.stButton > button { text-align: center !important; }
.ox-intro h1, .ox-verdict-title, .ox-section h3 { letter-spacing: 0; }
.ox-list li { padding: 0.7rem 1.4rem 0.7rem 0; }
.ox-list li::before { left: auto; right: 0.2rem; }
.ox-tech b, .ox-tech small { text-align: right; }
</style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Top bar (brand on one side, language switch on the other)
# ---------------------------------------------------------------------

brand_col, lang_col = st.columns([4, 1.4], vertical_alignment="center")

with brand_col:
    md(
        f"""
        <div class="ox-top">
            <div class="ox-logo">◈</div>
            <div>
                <div class="ox-brand-name">ORACLE-X</div>
                <div class="ox-brand-tag">{esc(t("brand_tag"))}</div>
            </div>
        </div>
        """
    )

with lang_col:
    st.radio(
        "Language",
        list(LANG_OPTIONS.keys()),
        horizontal=True,
        key="lang_choice",
        label_visibility="collapsed",
    )

md(
    f"""
    <div class="ox-intro">
        <h1>{esc(t("h1"))}</h1>
        <p>{esc(t("intro"))}</p>
    </div>
    """
)


# ---------------------------------------------------------------------
# Incident picker
# ---------------------------------------------------------------------

with st.container(border=True):
    col_input, col_button = st.columns([1.2, 1], vertical_alignment="bottom")

    with col_input:
        incident_id = st.selectbox(
            t("choose_incident"),
            options=list(INCIDENT_NAMES.keys()),
            format_func=lambda n: t(
                "incident_item",
                n=n,
                title=INCIDENT_NAMES[n][1 if IS_AR else 0],
            ),
        )

    with col_button:
        run_investigation = st.button(
            t("run"),
            type="primary",
            use_container_width=True,
        )


# ---------------------------------------------------------------------
# Fetch (kept in session so the page does not reset on interaction)
# ---------------------------------------------------------------------

REQUIRED_SECTIONS = {
    "incident",
    "decision",
    "validation",
    "scenario_metrics",
    "llm_interpretation",
    "provenance",
}


def fetch_investigation(display_number):
    """Call the API. Returns (data, error_message)."""
    incident_number = display_number + API_ID_OFFSET
    try:
        with st.spinner(t("spinner")):
            response = requests.get(
                f"{API_URL}/investigate/{incident_number}/summary",
                timeout=120,
            )
    except requests.Timeout:
        return None, t("err_timeout")
    except requests.ConnectionError:
        return None, t("err_conn")
    except requests.RequestException as exc:
        return None, t("err_request", e=exc)

    if response.status_code == 404:
        return None, t("err_404", n=display_number)
    if response.status_code != 200:
        return None, t("err_http", c=response.status_code)

    try:
        data = response.json()
    except ValueError:
        return None, t("err_json")

    missing = REQUIRED_SECTIONS - set(data.keys())
    if missing:
        return None, t("err_missing", m=", ".join(sorted(missing)))

    return data, None


if run_investigation:
    data, error = fetch_investigation(int(incident_id))
    if error:
        st.session_state.pop("result", None)
        st.error(error)
    else:
        st.session_state["result"] = {"id": int(incident_id), "data": data}


# ---------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------

result = st.session_state.get("result")

if not result:
    section(t("how_title"))
    md(
        f"""
        <div class="ox-steps">
            <div class="ox-step"><b>{esc(t("s1_t"))}</b><span>{esc(t("s1_d"))}</span></div>
            <div class="ox-step"><b>{esc(t("s2_t"))}</b><span>{esc(t("s2_d"))}</span></div>
            <div class="ox-step"><b>{esc(t("s3_t"))}</b><span>{esc(t("s3_d"))}</span></div>
        </div>
        """
    )
    st.stop()


# ---------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------

data = result["data"]

# Arabic: translate the free-text parts of the answer (cached per text).
translation_state = "none"
translation_error = ""
if IS_AR:
    pending = collect_server_texts(data)
    if pending:
        try:
            with st.spinner(t("translating")):
                RUNTIME_TR.update(translate_to_arabic(tuple(pending)))
            translation_state = "ok"
        except Exception as exc:
            translation_state = "failed"
            translation_error = str(exc)[:160]

try:
    incident = data["incident"]
    decision = data["decision"]
    validation = data["validation"]
    metrics = data["scenario_metrics"]
    root_cause = data.get("root_cause_analysis", {}) or {}
    llm = data["llm_interpretation"]
    provenance = data["provenance"]

    # ---- Verdict -----------------------------------------------------

    chips = (
        chip(pretty(incident.get("severity")), tone_for(incident.get("severity")), t("severity"))
        + chip(pretty(decision.get("status")), tone_for(decision.get("status")), t("decision"))
        + chip(pretty(validation.get("status")), tone_for(validation.get("status")), t("checks"))
        + chip(pretty(incident.get("source_type")), tone_for(incident.get("source_type")), t("data"))
    )

    section(t("result"), t("result_sub", n=result["id"]))

    if IS_AR and translation_state == "failed":
        md(f"<div class='ox-note'>{esc(t('ar_note'))}</div>")
        if translation_error:
            md(f"<div class='ox-note' dir='ltr' style='text-align:left'>Translation error: {esc(translation_error)}</div>")
    elif IS_AR and translation_state == "ok":
        md(f"<div class='ox-note'>{esc(t('tr_note'))}</div>")

    md(
        f"""
        <div class="ox-verdict">
            <div class="ox-incident-id">{esc(t("incident", n=result["id"]))}</div>
            <div class="ox-verdict-title">{bidi(dyn(incident.get("title")))}</div>
            <div class="ox-verdict-sub">{bidi(dyn(incident.get("summary")))}</div>
            <div class="ox-chips">{chips}</div>
            <div class="ox-action">
                <div class="ox-action-label">{esc(t("what_to_do"))}</div>
                <div class="ox-action-text">{bidi(dyn(decision.get("recommended_action")))}</div>
                <div class="ox-action-why">
                    <strong>{esc(t("why"))}</strong> {bidi(dyn(decision.get("rationale")))}
                </div>
            </div>
        </div>
        """
    )

    # ---- Numbers -----------------------------------------------------

    demand = metrics.get("demand", {})
    inventory = metrics.get("inventory", {})
    financial = metrics.get("financial", {})
    customer = metrics.get("customer", {})

    section(t("numbers"), t("numbers_sub"))

    md(
        '<div class="ox-metrics">'
        + metric_card(
            t("orders"),
            f"{num(demand, 'simulated_daily_orders'):,.0f}",
            f"{num(demand, 'change_pct'):+.1f}%",
            num(demand, "change_pct"),
            t("scenario"),
            "warn",
        )
        + metric_card(
            t("stock"),
            t("days", v=f"{num(inventory, 'simulated_cover_days'):.1f}"),
            f"{-num(inventory, 'decline_pct'):+.1f}%",
            -num(inventory, "decline_pct"),
            t("estimated"),
            "info",
        )
        + metric_card(
            t("revenue"),
            f"${num(financial, 'current_daily_revenue'):,.0f}",
            f"{num(financial, 'change_pct'):+.1f}%",
            num(financial, "change_pct"),
            t("scenario"),
            "warn",
        )
        + metric_card(
            t("reviews"),
            f"{num(customer, 'current_review_score'):.2f} / 5",
            f"{num(customer, 'change'):+.2f}",
            num(customer, "change"),
            t("scenario"),
            "warn",
        )
        + "</div>"
    )

    md(f"<div class='ox-note'>{esc(t('metrics_note'))}</div>")

    # ---- Likely causes ----------------------------------------------

    candidates = root_cause.get("candidate_causes", []) or []

    if candidates:
        section(t("causes"), t("causes_sub"))

        cards = ""
        for c in candidates:
            cards += f"""
            <div class="ox-cause">
                <div class="ox-cause-head">
                    <div class="ox-cause-title">{bidi(dyn(c.get("candidate_cause")))}</div>
                    {confidence_meter(c.get("confidence"))}
                </div>
                <div class="ox-cause-block">
                    <b>{esc(t("supports"))}</b>
                    <span>{bidi(dyn(c.get("evidence_for")))}</span>
                </div>
                <div class="ox-cause-block">
                    <b>{esc(t("holds_back"))}</b>
                    <span>{bidi(dyn(c.get("evidence_against")))}</span>
                </div>
                <div class="ox-cause-type">
                    {chip(pretty(c.get("evidence_type")), "neutral", t("evidence"))}
                </div>
            </div>
            """
        md(f'<div class="ox-causes">{cards}</div>')

    # ---- Plain-words summary ----------------------------------------

    section(t("plain"))
    md(
        f"""
        <div class="ox-plain">
            <p>{bidi(dyn(llm.get("executive_summary")))}</p>
            <small>{esc(t("plain_note"))}</small>
        </div>
        """
    )

    # ---- Details -----------------------------------------------------

    section(t("details"), t("details_sub"))

    tab_seen, tab_unsure, tab_open, tab_sources, tab_tech = st.tabs(
        [t("tab_seen"), t("tab_unsure"), t("tab_open"), t("tab_sources"), t("tab_tech")]
    )

    with tab_seen:
        md(items_html(llm.get("key_observations", []), t("no_obs")))

    with tab_unsure:
        md(items_html(llm.get("uncertainty", []), t("no_unc")))

    with tab_open:
        md(items_html(llm.get("unresolved_questions", []), t("no_q")))

    with tab_sources:
        if provenance:
            rows = ""
            for source, label in provenance.items():
                rows += f"""
                <div class="ox-source">
                    <span>{esc(pretty(source))}</span>
                    {chip(pretty(label), tone_for(label))}
                </div>
                """
            md(
                f"<div class='ox-note' style='margin-top:0.8rem'>{esc(t('src_note'))}</div>"
                f"<div class='ox-sources'>{rows}</div>"
            )
        else:
            md(f"<div class='ox-empty-line'>{esc(t('no_src'))}</div>")

    with tab_tech:
        rca_check = root_cause.get("validation", {}) or {}
        md(
            f"""
            <div class="ox-tech">
                <div><small>{esc(t("ai_status"))}</small><b>{esc(pretty(llm.get("status")))}</b></div>
                <div><small>{esc(t("ai_model"))}</small><b>{esc(llm.get("model"))}</b></div>
                <div><small>{esc(t("ai_perm"))}</small><b>{esc(t("read_only"))}</b></div>
                <div><small>{esc(t("rule_based"))}</small><b>{esc(pretty(rca_check.get("deterministic", "n/a")))}</b></div>
                <div><small>{esc(t("claims_cert"))}</small><b>{esc(pretty(rca_check.get("causal_certainty_claimed", "n/a")))}</b></div>
                <div><small>{esc(t("hist_used"))}</small><b>{esc(pretty(rca_check.get("historical_context_available", "n/a")))}</b></div>
            </div>
            <div class="ox-callout">{esc(t("tech_callout"))}</div>
            """
        )

    # ---- Footer ------------------------------------------------------

    md(f"<div class='ox-footer'>{esc(t('footer'))}</div>")

except KeyError as exc:
    st.error(t("err_field", e=exc))
except Exception as exc:
    st.error(t("err_unexpected", e=exc))
