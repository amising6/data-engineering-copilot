import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Configure the page layout
st.set_page_config(page_title="DE Copilot - STTM Engine", layout="centered", page_icon="🛠️")

st.title("🛠️ STTM-to-Code Factory")
st.write("Upload your Source-to-Target Mapping sheet to compile production code pipelines instantly.")

# 1. Downloadable Sample Template for Users
sample_data = {
    "Source_Table": ["src_users", "src_users", "src_users"],
    "Source_Column": ["user_id", "raw_phone", "created_at"],
    "Target_Table": ["dim_customers", "dim_customers", "dim_customers"],
    "Target_Column": ["customer_id", "cleaned_phone", "row_insert_dt"],
    "Transformation_Rule": [
        "Direct mapping", 
        "Strip whitespace, add +1 prefix if missing", 
        "Convert to UTC timestamp"
    ]
}
sample_df = pd.DataFrame(sample_data)

st.download_button(
    label="📥 Download Sample STTM Template",
    data=sample_df.to_csv(index=False),
    file_name="sample_sttm.csv",
    mime="text/csv"
)

st.write("---")

# 2. Language Selection Target Options
output_language = st.radio(
    "🎯 Select Target Output Language:",
    ["PySpark", "Snowflake SQL"],
    horizontal=True
)

st.write("---")

# 3. File Uploader Component
uploaded_file = st.file_uploader("Upload your completed mapping schema (CSV):", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV into memory
    df = pd.read_csv(uploaded_file)
    st.write("### 📋 Uploaded Mapping Schema:")
    st.dataframe(df)
    
    # 4. Execution Trigger
    if st.button(f"🚀 Compile {output_language} Code"):
        with st.spinner(f"Analyzing rules and compiling {output_language} pipeline..."):
            try:
                # Convert the dataframe to a clean string format for the AI prompt
                sttm_payload = df.to_string()
                
                # Secure API instantiation via Streamlit secrets
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                # Configure prompts and filenames based on user language choice
                if output_language == "PySpark":
                    output_filename = "compiled_pipeline.py"
                    editor_lang = "python"
                    system_prompt = """
                    You are an expert Data Architect specializing in Apache Spark code generation.
                    Your task is to read a Source-to-Target Mapping (STTM) layout and generate clean, optimized, production-ready PySpark code.
                    
                    Rules:
                    1. Handle all column renaming and transformations precisely as defined in the Transformation_Rule.
                    2. Output ONLY the executable PySpark code block. Do not include introductory prose, conclusions, or markdown wrappers like ```python.
                    """
                else: # Snowflake SQL
                    output_filename = "compiled_pipeline.sql"
                    editor_lang = "sql"
                    system_prompt = """
                    You are an expert Data Architect specializing in Snowflake ANSI SQL code generation.
                    Your task is to read a Source-to-Target Mapping (STTM) layout and generate a clean, optimized, production-ready SELECT transformation query or MERGE statement.
                    
                    Rules:
                    1. Handle all column renames using appropriate SQL aliases (AS) and transformations precisely as defined in the Transformation_Rule.
                    2. Output ONLY the executable raw SQL code. Do not include introductory prose, conclusions, or markdown wrappers like ```sql.
                    """
                
                # Call OpenAI service
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate {output_language} code for this mapping schema:\n\n{sttm_payload}"}
                    ],
                    temperature=0.1
                )
                
                generated_code = response.choices[0].message.content.strip()
                
                # ────────── PHYSICAL FILE GENERATION ──────────
                # Writes the specific file extension (.py or .sql) dynamically to your local directory
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(generated_code)
                # ───────────────────────────────────────────────
                
                # Display output in the browser interface
                st.write(f"### 💻 Compiled {output_language} Output:")
                st.code(generated_code, language=editor_lang)
                
                # Visual verification for you that the file hit the disk
                st.success(f"💾 File successfully generated and saved to your project folder as: `{output_filename}`")
                
            except KeyError:
                st.error("❌ Missing `OPENAI_API_KEY` inside your local `.streamlit/secrets.toml` file.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")