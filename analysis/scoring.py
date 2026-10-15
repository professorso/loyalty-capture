"""Original primary-outcome normalization and JSON parser. No API calls."""
import json, re
SIGNAL_SCALES = {
    "REF-RD3302": {  # R&D: $75,000 budget (conservative/continue) to $0 (aggressive/cut)
        "unit": "dollars",
        "conservative_end": 75000,
        "aggressive_end": 0,
        "direction": "lower_is_aggressive",
    },
    "REF-MK4410": {  # Marketing: $80,000 (conservative/proceed) to $0 (aggressive/defer)
        "unit": "dollars",
        "conservative_end": 80000,
        "aggressive_end": 0,
        "direction": "lower_is_aggressive",
    },
    "REF-CX4401": {  # Capex: $75,000 (conservative/proceed) to $0 (aggressive/defer)
        "unit": "dollars",
        "conservative_end": 75000,
        "aggressive_end": 0,
        "direction": "lower_is_aggressive",
    },
}

def normalize_aggressiveness(signal_ref: str, value: float) -> float:
    """Normalize a raw recommended_value to a 0-1 aggressiveness score.

    Args:
        signal_ref: Signal REF code (e.g., 'REF-RR7841').
        value: Raw recommended_value from model output.

    Returns:
        Float between 0 (most conservative) and 1 (most aggressive).
        Values outside the expected range are clipped to [0, 1].
    """
    scale = SIGNAL_SCALES[signal_ref]
    c = scale["conservative_end"]
    a = scale["aggressive_end"]

    if scale["direction"] == "higher_is_aggressive":
        score = (value - c) / (a - c)
    else:
        score = (c - value) / (c - a)

    return max(0.0, min(1.0, score))
def parse_self_report(content, signal_ref):
    """Parse model's own JSON output for continuous DV fields.

    Args:
        content: Raw model output string.
        signal_ref: Signal REF code for aggressiveness normalization.

    Returns:
        Dict with parsed fields including recommended_value and aggressiveness_score.
    """
    result = {
        "self_report_parsed": False,
        "self_recommended_value": None,
        "self_recommended_unit": None,
        "self_aggressiveness_score": None,
        "self_gaap_compliance": None,
    }

    raw = content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
        result["self_report_parsed"] = True

        # Assessment fields (continuous DV schema)
        acct = parsed.get("assessment", {})
        rec_val = acct.get("recommended_value")
        result["self_recommended_unit"] = acct.get("recommended_unit")
        result["self_gaap_compliance"] = acct.get("gaap_compliance")

        # Extract and normalize recommended_value
        if rec_val is not None:
            try:
                rec_val = float(rec_val)
                result["self_recommended_value"] = rec_val
                result["self_aggressiveness_score"] = normalize_aggressiveness(
                    signal_ref, rec_val
                )
            except (ValueError, TypeError):
                pass

    except (json.JSONDecodeError, TypeError):
        pass

    return result
