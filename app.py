import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import load_uploaded_data, clean_dataframe, build_data_quality_report, workbook_sheets
from eligibility_engine import match_assistance_rules, assess_insurance, calculate_financing_gap

st.set_page_config(page_title="AapdaSetu | Disaster Recovery", page_icon="🌧️", layout="wide")

st.title("AapdaSetu")
st.subheader("Bridging the Disaster Recovery Financing Gap through an Eligibility-Matching Framework")
st.caption("Insurance and Government Assistance in Urban India | Mumbai urban flooding case study: 8 July 2024")

st.info(
    "Academic research prototype and decision-support application. Outputs are indicative, "
    "based on uploaded/reference data and predefined criteria, and are not official government "
    "decisions, confirmed insurance coverage, or guaranteed assistance."
)

with st.sidebar:
    st.header("Data inputs")
    uploaded = st.file_uploader(
        "Upload CSV or Excel data",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False,
        help="You can upload your research workbook or an individual data table."
    )
    st.divider()
    st.caption("No live government database is connected. Use verified secondary sources and cite them.")

if uploaded is not None:
    raw_df, sheet_name = load_uploaded_data(uploaded)
    st.success(f"Loaded: {uploaded.name}" + (f" — worksheet: {sheet_name}" if sheet_name else ""))
else:
    raw_df = None

tabs = st.tabs(["Dashboard", "Data cleaning", "Eligibility matching", "Financing gap", "Method & limitations"])

with tabs[0]:
    st.markdown("### Research overview")
    if raw_df is not None:
        df = clean_dataframe(raw_df)
        report = build_data_quality_report(df)
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", f"{len(df.columns):,}")
        c3.metric("Duplicate rows", f"{report['duplicate_rows']:,}")
        st.dataframe(df.head(100), use_container_width=True)
    else:
        st.write("Upload your research workbook or a CSV table to display its data.")
        st.markdown(
            "- Review event evidence and source coverage.\n"
            "- Explore assistance rules and insurance conditions.\n"
            "- Run a transparent preliminary matching assessment."
        )

with tabs[1]:
    st.markdown("### Data cleaning and quality checks")
    if raw_df is None:
        st.warning("Upload a CSV or Excel file to begin.")
    else:
        cleaned = clean_dataframe(raw_df)
        quality = build_data_quality_report(cleaned)
        a, b, c = st.columns(3)
        a.metric("Rows after cleaning", len(cleaned))
        b.metric("Columns", len(cleaned.columns))
        c.metric("Duplicate rows", quality["duplicate_rows"])
        st.write("Cleaning actions are conservative: column labels and whitespace are normalized, "
                 "blank rows/columns are removed, and exact duplicate rows are identified. "
                 "No missing financial values are automatically imputed.")
        st.dataframe(cleaned, use_container_width=True)
        st.download_button(
            "Download cleaned CSV",
            data=cleaned.to_csv(index=False).encode("utf-8-sig"),
            file_name="aapdasetu_cleaned_data.csv",
            mime="text/csv"
        )
        st.markdown("#### Missing values by column")
        miss = cleaned.isna().sum().rename("Missing_Count").to_frame()
        miss["Missing_Percent"] = (miss["Missing_Count"] / max(len(cleaned), 1) * 100).round(2)
        st.dataframe(miss, use_container_width=True)

with tabs[2]:
    st.markdown("### Preliminary eligibility and scheme matching")
    st.caption("Use the rule table below as a demonstration. Enter only rules verified from the relevant official scheme documents.")
    st.markdown("#### Applicant / loss profile")
    col1, col2, col3 = st.columns(3)
    with col1:
        applicant_type = st.selectbox("Applicant category", ["Household", "Small business", "Other"])
        disaster_type = st.selectbox("Disaster type", ["Urban flood", "Heavy rain", "Waterlogging", "Other"])
    with col2:
        state = st.text_input("State", value="Maharashtra")
        district = st.text_input("District / city", value="Mumbai")
    with col3:
        loss_type = st.selectbox("Loss category", ["House damage", "Contents", "Business interruption", "Other"])
        loss_amount = st.number_input("Reported / estimated loss (INR)", min_value=0.0, value=0.0, step=1000.0)

    st.markdown("#### Reference assistance rules")
    default_rules = pd.DataFrame([
        {"Scheme": "Example rule — replace with verified scheme", "Applicant_Type": "Household",
         "Disaster_Type": "Urban flood", "Loss_Category": "House damage",
         "Criterion": "Illustrative only; enter official eligibility conditions",
         "Potential_Assistance_INR": 0, "Source": "", "Effective_Date": "", "Verified": False}
    ])
    rules_input = st.data_editor(default_rules, num_rows="dynamic", use_container_width=True, key="rules_editor")
    if st.button("Run preliminary matching", type="primary"):
        matches = match_assistance_rules(
            applicant_type=applicant_type,
            disaster_type=disaster_type,
            loss_category=loss_type,
            loss_amount=loss_amount,
            rules=rules_input
        )
        if matches.empty:
            st.warning("No matching rule found. This does not establish ineligibility; the reference rules may be incomplete.")
        else:
            st.dataframe(matches, use_container_width=True)
            st.caption("A match is an indicative criteria-based match. Verification and final decisions remain with relevant authorities.")

with tabs[3]:
    st.markdown("### Insurance and financing gap assessment")
    st.write("Use amounts supported by event-specific sources or applicant-provided policy/claim evidence. Do not treat industry-wide premiums as event-specific claim payments.")
    x1, x2, x3 = st.columns(3)
    with x1:
        assessed_loss = st.number_input("Reported / estimated loss (INR)", min_value=0.0, value=0.0, step=1000.0, key="gap_loss")
    with x2:
        potential_insurance = st.number_input("Potential insurance payment (INR)", min_value=0.0, value=0.0, step=1000.0)
    with x3:
        potential_assistance = st.number_input("Potential government assistance (INR)", min_value=0.0, value=0.0, step=1000.0)
    if st.button("Calculate indicative financing gap"):
        result = calculate_financing_gap(assessed_loss, potential_insurance, potential_assistance)
        st.metric("Indicative residual financing gap", f"₹{result:,.2f}")
        st.caption("This simple calculation assumes the amounts are comparable, loss-specific, and not double-counted. Confirm policy terms, scheme conditions, and payment status.")

with tabs[4]:
    st.markdown("### Methodology and limitations")
    st.markdown("""
**Method:** transparent rule-based criteria matching against user-uploaded or manually configured reference data.

**Data principles**
- Keep the original source, date, geography, unit, and reporting period with each observation.
- Do not combine aggregate state-level figures with Mumbai-only household-level figures as if they were the same population.
- Distinguish budget allocations, releases, sanctioned assistance, and actual payments.
- Distinguish insurance premiums, reported claims, assessed claims, and settled claims.
- Preserve missing values as missing unless a documented and defensible method supports an estimate.

**Interpretation:** AapdaSetu provides a preliminary eligibility indication and prototype-generated estimate. The outputs are not official decisions or guaranteed assistance. Further validation with official rules, data, and institutions is required.
""")
