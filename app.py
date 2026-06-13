import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="DE Copilot - Enterprise STTM Factory",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ DE Copilot - Enterprise STTM Factory")
st.subheader("Transform Retail STTM into Snowflake DDL, SQL, Data Dictionary, Technical Specs and DQ Rules")

uploaded_file = st.file_uploader(
    "Upload Retail Enterprise STTM",
    type=["csv"]
)

REQUIRED_COLUMNS = [
    "Source_Table",
    "Source_Column",
    "Target_Table",
    "Target_Column",
    "Data_Type",
    "Nullable",
    "Primary_Key_Flag",
    "Audit_Flag",
    "Business_Definition",
    "Transformation_Rule",
    "DQ_Rule"
]


def validate_sttm(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


def generate_ddl(df):
    target_table = df["Target_Table"].iloc[0]
    lines = [f"CREATE OR REPLACE TABLE {target_table} ("]

    column_defs = []

    for _, row in df.iterrows():
        nullable = "NOT NULL" if str(row["Nullable"]).upper() == "N" else ""
        column_defs.append(
            f"    {row['Target_Column']} {row['Data_Type']} {nullable}".strip()
        )

    lines.append(",\n".join(column_defs))
    lines.append(");")
    return "\n".join(lines)


def transform_expression(row):
    source_col = row["Source_Column"]
    target_col = row["Target_Column"]
    rule = str(row["Transformation_Rule"]).lower()

    if str(row["Source_Table"]).upper() == "SYSTEM":
        return f"CURRENT_TIMESTAMP() AS {target_col}"

    if "lowercase" in rule and "trim" in rule:
        return f"LOWER(TRIM({source_col})) AS {target_col}"

    if "trim" in rule:
        return f"TRIM({source_col}) AS {target_col}"

    if "uppercase" in rule:
        return f"UPPER({source_col}) AS {target_col}"

    if "date" in rule:
        return f"TO_DATE({source_col}) AS {target_col}"

    if "remove spaces and hyphens" in rule:
        return f"REPLACE(REPLACE({source_col}, ' ', ''), '-', '') AS {target_col}"

    return f"{source_col} AS {target_col}"


def generate_sql(df):
    target_table = df["Target_Table"].iloc[0]
    source_table = df[df["Source_Table"].str.upper() != "SYSTEM"]["Source_Table"].iloc[0]

    expressions = [transform_expression(row) for _, row in df.iterrows()]

    sql = f"INSERT INTO {target_table}\nSELECT\n"
    sql += ",\n".join([f"    {expr}" for expr in expressions])
    sql += f"\nFROM {source_table};"

    return sql


def generate_data_dictionary(df):
    return df[[
        "Target_Column",
        "Data_Type",
        "Nullable",
        "Primary_Key_Flag",
        "Business_Definition"
    ]]


def generate_technical_spec(df):
    spec = "# Technical Mapping Specification\n\n"

    for _, row in df.iterrows():
        spec += f"## {row['Target_Column']}\n\n"
        spec += f"- Source Table: {row['Source_Table']}\n"
        spec += f"- Source Column: {row['Source_Column']}\n"
        spec += f"- Target Table: {row['Target_Table']}\n"
        spec += f"- Target Column: {row['Target_Column']}\n"
        spec += f"- Data Type: {row['Data_Type']}\n"
        spec += f"- Nullable: {row['Nullable']}\n"
        spec += f"- Primary Key: {row['Primary_Key_Flag']}\n"
        spec += f"- Audit Field: {row['Audit_Flag']}\n"
        spec += f"- Business Definition: {row['Business_Definition']}\n"
        spec += f"- Transformation Rule: {row['Transformation_Rule']}\n"
        spec += f"- DQ Rule: {row['DQ_Rule']}\n\n"

    return spec


def generate_dq_rules(df):
    target_table = df["Target_Table"].iloc[0]
    dq_sql = []

    dq_sql.append(f"-- Data Quality Rules for {target_table}\n")

    for _, row in df.iterrows():
        col = row["Target_Column"]
        dq_rule = str(row["DQ_Rule"]).upper()
        pk = str(row["Primary_Key_Flag"]).upper()
        nullable = str(row["Nullable"]).upper()

        if nullable == "N" or "NOT NULL" in dq_rule:
            dq_sql.append(f"""
-- NOT NULL Check: {col}
SELECT
    '{col}' AS column_name,
    COUNT(*) AS failed_count
FROM {target_table}
WHERE {col} IS NULL;
""")

        if pk == "Y":
            dq_sql.append(f"""
-- Duplicate Check: {col}
SELECT
    {col},
    COUNT(*) AS record_count
FROM {target_table}
GROUP BY {col}
HAVING COUNT(*) > 1;
""")

        if "VALID EMAIL" in dq_rule:
            dq_sql.append(f"""
-- Email Format Check: {col}
SELECT
    {col}
FROM {target_table}
WHERE {col} IS NOT NULL
  AND NOT REGEXP_LIKE({col}, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$');
""")

        if "VALID DATE" in dq_rule:
            dq_sql.append(f"""
-- Future Date Check: {col}
SELECT
    {col}
FROM {target_table}
WHERE {col} > CURRENT_DATE();
""")

        if "VALID CODE" in dq_rule:
            dq_sql.append(f"""
-- Valid Code Check: {col}
-- Replace values below with approved business reference values
SELECT
    {col}
FROM {target_table}
WHERE {col} IS NOT NULL
  AND {col} NOT IN ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM');
""")

    return "\n".join(dq_sql)


if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.success("STTM Uploaded Successfully")

    missing_columns = validate_sttm(df)

    if missing_columns:
        st.error("Missing required columns:")
        st.write(missing_columns)
        st.stop()

    st.subheader("Uploaded STTM")
    st.dataframe(df, use_container_width=True)

    if st.button("🏗️ Generate Data Product Assets"):
        ddl = generate_ddl(df)
        sql = generate_sql(df)
        dictionary = generate_data_dictionary(df)
        tech_spec = generate_technical_spec(df)
        dq_rules = generate_dq_rules(df)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Snowflake DDL",
            "Snowflake SQL",
            "Data Dictionary",
            "Technical Spec",
            "DQ Rules"
        ])

        with tab1:
            st.code(ddl, language="sql")
            st.download_button("Download DDL", ddl, file_name="snowflake_ddl.sql")

        with tab2:
            st.code(sql, language="sql")
            st.download_button("Download SQL", sql, file_name="snowflake_insert.sql")

        with tab3:
            st.dataframe(dictionary, use_container_width=True)
            csv = dictionary.to_csv(index=False)
            st.download_button("Download Data Dictionary", csv, file_name="data_dictionary.csv")

        with tab4:
            st.markdown(tech_spec)
            st.download_button("Download Technical Spec", tech_spec, file_name="technical_spec.md")

        with tab5:
            st.code(dq_rules, language="sql")
            st.download_button("Download DQ Rules", dq_rules, file_name="dq_rules.sql")

        st.success("Data Product Assets Generated Successfully")
else:
    st.info("Upload an STTM CSV to begin.")