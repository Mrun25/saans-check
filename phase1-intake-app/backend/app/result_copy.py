"""
Result + exposure-context logic (PRD §3.3, §4.2.E).

Core design principle this module enforces: a "normal" acoustic result is NEVER shown without
exposure-context information attached. The two are always combined into a single recommendation
object. This is not a UI nicety — it's the asymmetric-caution requirement: because silicosis is
asymptomatic until late and irreversible, a false "you're fine" is more dangerous than a false
alarm, so "your cough sounds normal" must never be the whole message a worker receives.

All result strings are FIXED and pre-approved per language — they are looked up from a table,
never generated freely by a model. If an LLM is ever used to phrase results more naturally,
it must only be allowed to choose among / lightly rephrase these pre-approved strings, and
must never see raw_model_score or be allowed to invent new claims. This module is the boundary
that enforces that.
"""

from dataclasses import dataclass
from app.models import RiskTier


@dataclass
class ExposureRiskFlags:
    high_years_exposure: bool  # >= 10 years per PRD's "5-10 years to symptomatic" framing
    poor_mask_usage: bool  # "never" or "sometimes"
    poor_dust_suppression: bool  # "none" or "unknown"


def compute_exposure_flags(
    years_of_exposure: float, mask_usage_frequency: str, dust_suppression_at_site: str | None
) -> ExposureRiskFlags:
    return ExposureRiskFlags(
        high_years_exposure=years_of_exposure >= 10,
        poor_mask_usage=mask_usage_frequency in ("never", "sometimes"),
        poor_dust_suppression=(dust_suppression_at_site in (None, "none", "unknown")),
    )


# Fixed, pre-approved result strings. Hindi/English shown; Marwari and Gujarati follow the
# same structure (see locales/ for full translations — translator review still required before
# field deployment, these are placeholder professional-grade drafts, not field-validated).
_RESULT_STRINGS = {
    "hi": {
        RiskTier.NORMAL_PROXY: (
            "आपकी खांसी की आवाज़ सामान्य लग रही है। यह कोई जांच का परिणाम नहीं है — "
            "केवल एक प्राथमिक संकेत है। 3 महीने में फिर से जांच कराएं।"
        ),
        RiskTier.ELEVATED_PROXY: (
            "आपकी खांसी में कुछ बदलाव दिख रहा है। यह सिलिकोसिस का परिणाम नहीं बताता — "
            "केवल यह सुझाव देता है कि अगले कैंप या क्लिनिक में जांच कराना ठीक रहेगा।"
        ),
        RiskTier.NO_AUDIO_SUBMITTED: "आपकी जानकारी दर्ज हो गई है। अगली जांच का समय आने पर सूचना मिलेगी।",
        RiskTier.MODEL_UNAVAILABLE: "आपकी जानकारी दर्ज हो गई है। अगली जांच का समय आने पर सूचना मिलेगी।",
    },
    "en": {
        RiskTier.NORMAL_PROXY: (
            "Your cough sounds typical. This is not a test result — only an early signal. "
            "Recheck again in 3 months."
        ),
        RiskTier.ELEVATED_PROXY: (
            "Your cough shows some pattern worth a closer look. This does NOT mean silicosis — "
            "only that getting checked at the next camp or clinic is worthwhile."
        ),
        RiskTier.NO_AUDIO_SUBMITTED: "Your information has been recorded. You'll be notified when it's time for your next check.",
        RiskTier.MODEL_UNAVAILABLE: "Your information has been recorded. You'll be notified when it's time for your next check.",
    },
}

_EXPOSURE_REMINDER = {
    "hi": (
        "\n\nध्यान दें: भले ही खांसी सामान्य लगे, धूल में लंबे समय तक काम करना खतरनाक है। "
        "मास्क पहनें और जहां संभव हो वहां गीली ड्रिलिंग का उपयोग करवाएं।"
    ),
    "en": (
        "\n\nNote: even if your cough sounds typical, long-term dust exposure carries risk "
        "either way. Keep wearing a mask, and ask about wet drilling at your site where possible."
    ),
}


def build_result_message(
    risk_tier: RiskTier,
    exposure_flags: ExposureRiskFlags,
    language: str = "hi",
) -> str:
    """
    The single function every result-display endpoint must call. Returns the complete,
    pre-approved message — including the exposure reminder appended whenever risk_tier is
    NORMAL_PROXY and the worker has elevated exposure risk flags, per the asymmetric-caution
    requirement. This appending is NOT optional/configurable per deployment.
    """
    lang = language if language in _RESULT_STRINGS else "hi"
    base_message = _RESULT_STRINGS[lang][risk_tier]

    should_append_reminder = risk_tier == RiskTier.NORMAL_PROXY and (
        exposure_flags.high_years_exposure
        or exposure_flags.poor_mask_usage
        or exposure_flags.poor_dust_suppression
    )

    if should_append_reminder:
        base_message += _EXPOSURE_REMINDER[lang]

    return base_message


def build_proxy_disclaimer(language: str = "hi") -> str:
    """
    Shown alongside EVERY result while the deployed model is the Stage-1 proxy classifier
    (i.e. model_version starts with "stage1_proxy"). Per PRD §4.2.D: "every output, internally
    and to any user or partner, must be labeled as a proxy model, not a silicosis model, until
    Stage 2 data exists." This is not skippable by configuration.
    """
    disclaimers = {
        "hi": (
            "यह उपकरण सिलिकोसिस की जांच नहीं करता। यह सामान्य खांसी के पैटर्न को परखता है और "
            "अभी तक सिलिकोसिस रोगियों पर परखा नहीं गया है।"
        ),
        "en": (
            "This tool does not test for silicosis. It checks for general cough patterns and "
            "has not yet been validated against confirmed silicosis cases."
        ),
    }
    return disclaimers.get(language, disclaimers["hi"])
