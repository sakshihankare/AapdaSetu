import pandas as pd

def _norm(value):
    if pd.isna(value):
        return ""
    return str(value).strip().casefold()

def match_assistance_rules(applicant_type, disaster_type, loss_category, loss_amount, rules):
    """
    Match an applicant profile against configured reference rules.

    Expected columns:
      Scheme, Applicant_Type, Disaster_Type, Loss_Category,
      Criterion, Potential_Assistance_INR, Source, Effective_Date, Verified

    Rows not marked Verified=True are retained as illustrative/unverified matches,
    but are explicitly labeled. This is a prototype indication, not an official decision.
    """
    if rules is None or rules.empty:
        return pd.DataFrame()

    required = ["Scheme", "Applicant_Type", "Disaster_Type", "Loss_Category"]
    missing = [c for c in required if c not in rules.columns]
    if missing:
        raise ValueError("Rules table missing required columns: " + ", ".join(missing))

    checks = (
        rules["Applicant_Type"].map(_norm).isin(["", "all", _norm(applicant_type)]) &
        rules["Disaster_Type"].map(_norm).isin(["", "all", _norm(disaster_type)]) &
        rules["Loss_Category"].map(_norm).isin(["", "all", _norm(loss_category)])
    )
    matched = rules.loc[checks].copy()
    if matched.empty:
        return matched

    if "Potential_Assistance_INR" in matched.columns:
        matched["Potential_Assistance_INR"] = pd.to_numeric(
            matched["Potential_Assistance_INR"], errors="coerce"
        ).fillna(0).clip(lower=0)
        matched["Indicative_Amount_Capped_To_Loss_INR"] = matched[
            "Potential_Assistance_INR"
        ].clip(upper=max(float(loss_amount), 0))

    if "Verified" in matched.columns:
        matched["Rule_Status"] = matched["Verified"].apply(
            lambda x: "Source marked verified" if str(x).strip().casefold() in ("true", "1", "yes")
            else "Unverified / illustrative — validate source"
        )
    else:
        matched["Rule_Status"] = "Unverified / illustrative — validate source"

    matched["Assessment"] = "Potentially relevant criteria match"
    return matched.reset_index(drop=True)

def assess_insurance(policy_details, reported_loss):
    """
    Lightweight policy information check. Does not decide coverage.
    policy_details may include coverage_limit_inr, deductible_inr,
    flood_peril_included, policy_active_on_event, exclusions_reviewed.
    """
    details = policy_details or {}
    limit = max(float(details.get("coverage_limit_inr", 0) or 0), 0)
    deductible = max(float(details.get("deductible_inr", 0) or 0), 0)
    loss = max(float(reported_loss or 0), 0)
    peril = details.get("flood_peril_included")
    active = details.get("policy_active_on_event")
    exclusions = details.get("exclusions_reviewed")

    estimate = max(0.0, min(loss - deductible, limit))
    if peril is True and active is True and exclusions is True:
        status = "Policy inputs indicate possible coverage; insurer confirmation required"
    else:
        status = "Insufficient policy evidence to indicate coverage"

    return {
        "status": status,
        "prototype_estimated_amount_inr": estimate,
        "coverage_limit_inr": limit,
        "deductible_inr": deductible,
        "decision_note": "Not a claim approval, coverage confirmation, or settlement estimate."
    }

def calculate_financing_gap(loss_amount, potential_insurance, potential_assistance):
    """
    Compute a provisional gap from comparable, loss-specific amounts.
    Caller must avoid double-counting and confirm amounts are actual/appropriate.
    """
    loss = max(float(loss_amount or 0), 0)
    insurance = max(float(potential_insurance or 0), 0)
    assistance = max(float(potential_assistance or 0), 0)
    return max(0.0, loss - insurance - assistance)
