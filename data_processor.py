from io import BytesIO
import re
import pandas as pd

def _normalize_column_name(value):
    text = str(value).strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w]", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unnamed_column"

def load_uploaded_data(uploaded_file):
    """Load one CSV or Excel worksheet from a Streamlit UploadedFile."""
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df, None
    if name.endswith((".xlsx", ".xls")):
        excel = pd.ExcelFile(uploaded_file)
        sheet = excel.sheet_names[0]
        df = pd.read_excel(excel, sheet_name=sheet)
        return df, sheet
    raise ValueError("Supported formats are CSV, XLSX, and XLS.")

def workbook_sheets(uploaded_file):
    """Return sheet names for an Excel upload; return an empty list for CSV."""
    if not uploaded_file.name.lower().endswith((".xlsx", ".xls")):
        return []
    uploaded_file.seek(0)
    return pd.ExcelFile(uploaded_file).sheet_names

def clean_dataframe(df):
    """
    Conservative general cleaning:
    - trim string cells and column names
    - standardize column labels
    - remove completely empty rows/columns
    - remove exact duplicate rows
    - convert whitespace-only cells to missing
    Does not impute data or convert financial units without metadata.
    """
    if df is None:
        return pd.DataFrame()
    out = df.copy()
    out.columns = [_normalize_column_name(c) for c in out.columns]
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )
        out[col] = out[col].replace(r"^\s*$", pd.NA, regex=True)
    out = out.dropna(axis=0, how="all").dropna(axis=1, how="all")
    out = out.drop_duplicates().reset_index(drop=True)
    return out

def build_data_quality_report(df):
    df = df if df is not None else pd.DataFrame()
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()) if not df.empty else 0,
        "missing_by_column": df.isna().sum().to_dict(),
        "missing_percent_by_column": (
            (df.isna().mean() * 100).round(2).to_dict() if len(df) else {}
        ),
    }
