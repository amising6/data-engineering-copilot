import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DE Copilot - STTM Factory",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ DE Copilot - Enterprise STTM Factory")
st.subheader(
    "Transform Retail STTM into Snowflake DDL, SQL, Data Dictionary and Technical Specifications"
)

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def generate_ddl(df):

    ddl = "CREATE OR REPLACE TABLE DIM_CUSTOMER (\n"

    cols = []

    for _, row in df.iterrows():

        col_name = row["Target_Column"]
        data_type = row["Data_Type"]

        if str(row["Nullable"]).upper() == "N":
            cols.append(f"    {col_name} {data_type} NOT NULL")
        else:
            cols.append(f"    {col_name} {data_type}")

    ddl += ",\n".join(cols)
    ddl += "\n);"

    return ddl


def generate_sql(df):

    sql = "INSERT INTO DIM_CUSTOMER\nSELECT\n"

    transformations = []

    for _, row in df.iterrows():

        source_col = row["Source_Column"]
        target_col = row["Target_Column"]

        rule = str(row["Transformation_Rule"]).lower()

        if "trim whitespace" in rule:
            transformations.append(
                f"    TRIM({source_col}) AS {target_col}"
            )

        elif "lowercase" in rule:
            transformations.append(
                f"    LOWER(TRIM({source_col})) AS {target_col}"
            )

        elif "uppercase" in rule:
            transformations.append(
                f"    UPPER({source_col}) AS {target_col}"
            )

        elif "convert to date" in rule:
            transformations.append(
                f"    TO_DATE({source_col}) AS {target_col}"
            )

        elif "current timestamp" in rule:
            transformations.append(
                f"    CURRENT_TIMESTAMP() AS {target_col}"
            )

        else:
            transformations.append(
                f"    {source_col} AS {target_col}"
            )

    sql += ",\n".join(transformations)

    sql += "\nFROM SRC_CUSTOMER;"

    return sql


def generate_dictionary(df):

    dictionary = []

    dictionary.append(
        "| Target Column | Data Type | Business Definition |"
    )

    dictionary.append(
        "|---------------|-----------|--------------------|"
    )

    for _, row in df.iterrows():

        dictionary.append(
            f"| {row['Target_Column']} | "
            f"{row['Data_Type']} | "
            f"{row['Business_Definition']} |"
        )

    return "\n".join(dictionary)


def generate_tech_spec(df):

    output = "# Technical Mapping Specification\n\n"

    for _, row in df.iterrows():

        output += f"## {row['Target_Column']}\n\n"

        output += f"- Source Table: {row['Source_Table']}\n"
        output += f"- Source Column: {row['Source_Column']}\n"
        output += f"- Target Table: {row['Target_Table']}\n"
        output += f"- Target Column: {row['Target_Column']}\n"
        output += f"- Data Type: {row['Data_Type']}\n"
        output += f"- Nullable: {row['Nullable']}\n"
        output += f"- Business Definition: {row['Business_Definition']}\n"
        output += f"- Transformation Rule: {row['Transformation_Rule']}\n"
        output += f"- DQ Rule: {row['DQ_Rule']}\n\n"

    return output


# --------------------------------------------------
# Upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Retail Enterprise STTM",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.success("STTM Uploaded Successfully")

    st.write("### Uploaded STTM")

    st.dataframe(df)

    st.divider()

    if st.button("🏗️ Generate Data Product Assets"):

        ddl = generate_ddl(df)
        sql = generate_sql(df)
        dictionary = generate_dictionary(df)
        tech_spec = generate_tech_spec(df)

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Snowflake DDL",
                "Snowflake SQL",
                "Data Dictionary",
                "Technical Spec"
            ]
        )

        with tab1:
            st.code(ddl, language="sql")

            st.download_button(
                "Download DDL",
                ddl,
                file_name="snowflake_ddl.sql"
            )

        with tab2:
            st.code(sql, language="sql")

            st.download_button(
                "Download SQL",
                sql,
                file_name="snowflake_sql.sql"
            )

        with tab3:
            st.markdown(dictionary)

            st.download_button(
                "Download Data Dictionary",
                dictionary,
                file_name="data_dictionary.md"
            )

        with tab4:
            st.markdown(tech_spec)

            st.download_button(
                "Download Technical Spec",
                tech_spec,
                file_name="technical_spec.md"
            )

        st.success(
            "✅ Data Product Assets Generated Successfully"
        )