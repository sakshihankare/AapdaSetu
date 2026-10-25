import streamlit as st
import pandas as pd
import plotly.express as px

from data_processor import (
    load_uploaded_data,
    clean_dataframe,
    build_data_quality_report,
    workbook_sheets,
)
from eligibility_engine import (
    match_assistance_rules,
    assess_insurance,
    calculate_financing_gap,
)

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="AapdaSetu | Disaster Recovery",
    page_icon="🌧️",
    layout="wide",
)

# ---------------------------------------------------------
# VISUAL STYLE
# Keeps the existing horizontal navigation and dark theme.
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    h1 {
        font-size: 2.5rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.025em;
    }

    h2, h3 {
        font-weight: 650 !important;
        letter-spacing: -0.01em;
    }

    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 12px;
        padding: 14px 16px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    div[data-testid="stButton"] button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 10px;
        overflow: hidden;
    }

    .app-subtitle {
        color: #AAB4C3;
        font-size: 1rem;
        margin-top: -0.45rem;
        margin-bottom: 1rem;
    }

    .section-note {
        color: #AAB4C3;
        font-size: 0.92rem;
        margin-top: -0.45rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# APP HEADER
# ---------------------------------------------------------
st.title("🌧️ AapdaSetu")
st.subheader(
    "Bridging the Disaster Recovery Financing Gap through an "
    "Eligibility-Matching Framework"
)
st.markdown(
    '<div class="app-subtitle">'
    "Insurance and Government Assistance in Urban India "
    "| Mumbai urban flooding case study: 8 July 2024"
    "</div>",
    unsafe_allow_html=True,
)

st.info(
    "Academic research prototype and decision-support application. Outputs are "
    "indicative, based on uploaded/reference data and predefined criteria, and "
    "are not official government decisions, confirmed insurance coverage, or "
    "guaranteed assistance."
)

# ---------------------------------------------------------
# DATA INPUTS
# ---------------------------------------------------------
with st.sidebar:
    st.header("Data inputs")
    uploaded = st.file_uploader(
        "Upload CSV or Excel data",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False,
        help="Upload your research workbook or an individual data table.",
    )
    st.divider()
    st.caption(
        "No live government database is connected. Use verified secondary "
        "sources and cite them."
    )

if uploaded is not None:
    raw_df, sheet_name = load_uploaded_data(uploaded)
    loaded_message = f"Loaded: {uploaded.name}"
    if sheet_name:
        loaded_message += f" — worksheet: {sheet_name}"
    st.success(loaded_message)
else:
    raw_df = None

# Keep the existing horizontal tab navigation.
tabs = st.tabs(
    [
        "Dashboard",
        "Data cleaning",
        "Eligibility matching",
        "Financing gap",
        "Method & limitations",
    ]
)

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
with tabs[0]:
    st.markdown("### Research overview")
    st.markdown(
        '<div class="section-note">'
        "A structured view of the event evidence, data coverage, and "
        "analytical workflow used in this research."
        "</div>",
        unsafe_allow_html=True,
    )

    overview_left, overview_right = st.columns([1.65, 1])

    with overview_left:
        st.markdown("#### Research focus")
        st.write(
            "AapdaSetu examines how insurance and government assistance "
            "may contribute to disaster recovery, and how an eligibility-based "
            "assessment can help examine the remaining financing requirement."
        )

    with overview_right:
        st.markdown("#### Case study")
        st.markdown(
            """
            **Event:** Mumbai urban flooding  
            **Date:** 8 July 2024  
            **Geography:** Mumbai, Maharashtra  
            **Approach:** Evidence-based eligibility matching
            """
        )

    st.divider()
    st.markdown("#### Dataset snapshot")

    if raw_df is not None:
        df = clean_dataframe(raw_df)
        report = build_data_quality_report(df)

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Records", f"{len(df):,}")
        metric2.metric("Variables", f"{len(df.columns):,}")
        metric3.metric("Duplicate rows", f"{report['duplicate_rows']:,}")

        st.markdown("#### Data preview")
        st.dataframe(
            df.head(100),
            use_container_width=True,
            hide_index=True,
        )
        if len(df) > 100:
            st.caption("Showing the first 100 rows of the cleaned dataset.")
    else:
        st.warning(
            "Upload your research workbook or a CSV table using the sidebar "
            "to view the dataset snapshot."
        )

    st.divider()
    st.markdown("#### Analytical workflow")

    workflow1, workflow2, workflow3 = st.columns(3)
    with workflow1:
        st.markdown("**01 · Data preparation**")
        st.caption("Review data quality, source coverage, and missing values.")
    with workflow2:
        st.markdown("**02 · Eligibility assessment**")
        st.caption("Compare an applicant profile with recorded assistance rules.")
    with workflow3:
        st.markdown("**03 · Financing gap**")
        st.caption("Examine loss, potential support, and residual recovery need.")

# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------
with tabs[1]:
    st.markdown("### Data cleaning and quality checks")
    st.markdown(
        '<div class="section-note">'
        "Review the prepared dataset and the quality indicators used in analysis."
        "</div>",
        unsafe_allow_html=True,
    )

    if raw_df is None:
        st.warning("Upload a CSV or Excel file to begin.")
    else:
        cleaned = clean_dataframe(raw_df)
        quality = build_data_quality_report(cleaned)

        a, b, c = st.columns(3)
        a.metric("Rows after cleaning", f"{len(cleaned):,}")
        b.metric("Columns", f"{len(cleaned.columns):,}")
        c.metric("Duplicate rows", f"{quality['duplicate_rows']:,}")

        st.write(
            "Cleaning actions are conservative: column labels and whitespace "
            "are normalized, blank rows/columns are removed, and exact duplicate "
            "rows are identified. No missing financial values are automatically "
            "imputed."
        )

        st.markdown("#### Cleaned data")
        st.dataframe(cleaned, use_container_width=True, hide_index=True)

        st.download_button(
            "Download cleaned CSV",
            data=cleaned.to_csv(index=False).encode("utf-8-sig"),
            file_name="aapdasetu_cleaned_data.csv",
            mime="text/csv",
        )

        st.markdown("#### Missing values by column")
        miss = cleaned.isna().sum().rename("Missing_Count").to_frame()
        miss["Missing_Percent"] = (
            miss["Missing_Count"] / max(len(cleaned), 1) * 100
        ).round(2)
        st.dataframe(miss, use_container_width=True)

# ---------------------------------------------------------
# ELIGIBILITY MATCHING
# ---------------------------------------------------------
with tabs[2]:
    st.markdown("### Preliminary eligibility and scheme matching")
    st.markdown(
        '<div class="section-note">'
        "Enter an applicant/loss profile and compare it with the assistance "
        "criteria recorded in the reference table."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Applicant / loss profile")
    col1, col2, col3 = st.columns(3)

    with col1:
        applicant_type = st.selectbox(
            "Applicant category",
            ["Household", "Small business", "Other"],
        )
        disaster_type = st.selectbox(
            "Disaster type",
            ["Urban flood", "Heavy rain", "Waterlogging", "Other"],
        )

    with col2:
        state = st.text_input("State", value="Maharashtra")
        district = st.text_input("District / city", value="Mumbai")

    with col3:
        loss_type = st.selectbox(
            "Loss category",
            ["House damage", "Contents", "Business interruption", "Other"],
        )
        loss_amount = st.number_input(
            "Reported / estimated loss (INR)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    st.divider()
    st.markdown("#### Reference assistance rules")
    st.caption(
        "Enter only criteria supported by the relevant official scheme "
        "documents. Illustrative entries should remain clearly identified."
    )

    default_rules = pd.DataFrame(
        [
            {
                "Scheme": "Example rule — replace with verified scheme",
                "Applicant_Type": "Household",
                "Disaster_Type": "Urban flood",
                "Loss_Category": "House damage",
                "Criterion": "Illustrative only; enter official eligibility conditions",
                "Potential_Assistance_INR": 0,
                "Source": "",
                "Effective_Date": "",
                "Verified": False,
            }
        ]
    )

    rules_input = st.data_editor(
        default_rules,
        num_rows="dynamic",
        use_container_width=True,
        key="rules_editor",
    )

    run_matching = st.button(
        "Run Eligibility Assessment",
        type="primary",
        use_container_width=True,
    )

    if run_matching:
        matches = match_assistance_rules(
            applicant_type=applicant_type,
            disaster_type=disaster_type,
            loss_category=loss_type,
            loss_amount=loss_amount,
            rules=rules_input,
        )

        st.markdown("#### Assessment results")

        if matches.empty:
            st.warning(
                "No matching rule found. This does not establish "
                "ineligibility; the reference rules may be incomplete."
            )
        else:
            st.dataframe(matches, use_container_width=True, hide_index=True)
            st.caption(
                "A match is an indicative criteria-based match. Verification "
                "and final decisions remain with relevant authorities."
            )

            with st.expander("How to interpret the assessment"):
                st.markdown(
                    """
                    - **Criteria match:** The applicant profile matches one or
                      more criteria recorded in the reference rules.
                    - **Verification:** Check the source and effective date
                      of the relevant scheme information.
                    - **Indicative assistance:** A possible amount based on
                      the recorded criteria, not a confirmed payment.
                    - **Final decision:** Eligibility and assistance decisions
                      remain with the relevant authorities.
                    """
                )

# ---------------------------------------------------------
# FINANCING GAP
# ---------------------------------------------------------
with tabs[3]:
    st.markdown("### Insurance and financing gap assessment")
    st.markdown(
        '<div class="section-note">'
        "Examine the relationship between reported loss, potential insurance, "
        "government assistance, and the residual financing requirement."
        "</div>",
        unsafe_allow_html=True,
    )

    st.write(
        "Use amounts supported by event-specific sources or applicant-provided "
        "policy/claim evidence. Do not treat industry-wide premiums as "
        "event-specific claim payments."
    )

    x1, x2, x3 = st.columns(3)

    with x1:
        assessed_loss = st.number_input(
            "Reported / estimated loss (INR)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            key="gap_loss",
        )

    with x2:
        potential_insurance = st.number_input(
            "Potential insurance payment (INR)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    with x3:
        potential_assistance = st.number_input(
            "Potential government assistance (INR)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

    if st.button("Calculate Indicative Financing Gap", type="primary"):
        result = calculate_financing_gap(
            assessed_loss,
            potential_insurance,
            potential_assistance,
        )
        st.metric("Indicative residual financing gap", f"₹{result:,.2f}")
        st.caption(
            "This simple calculation assumes the amounts are comparable, "
            "loss-specific, and not double-counted. Confirm policy terms, "
            "scheme conditions, and payment status."
        )

# ---------------------------------------------------------
# METHOD & LIMITATIONS
# ---------------------------------------------------------
with tabs[4]:
    st.markdown("### Methodology and limitations")

    st.markdown(
        """
        **Method:** Transparent rule-based criteria matching against
        user-uploaded or manually configured reference data.

        **Data principles**
        - Keep the original source, date, geography, unit, and reporting
          period with each observation.
        - Do not combine aggregate state-level figures with Mumbai-only
          household-level figures as if they were the same population.
        - Distinguish budget allocations, releases, sanctioned assistance,
          and actual payments.
        - Distinguish insurance premiums, reported claims, assessed claims,
          and settled claims.
        - Preserve missing values as missing unless a documented and
          defensible method supports an estimate.

        **Interpretation:** AapdaSetu provides a preliminary eligibility
        indication and prototype-generated estimate. The outputs are not
        official decisions or guaranteed assistance. Further validation
        with official rules, data, and institutions is required.
        """
    )
