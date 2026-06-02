import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="DE Copilot - STTM Engine", layout="centered")

st.title("🛠️ STTM-to-Code Factory")
st.write("Upload your Source-to-Target Mapping sheet to compile production PySpark instantly.")

# Sample Template
sample_data = {
    "Source_Table": ["src_users", "src_users"],
    "Source_Column": ["user_id", "raw_phone"],
    "Target_Table": ["dim_customers", "dim_customers"],
    "Target_Column": ["customer_id", "cleaned_phone"],
    "Transformation_Rule": ["Direct mapping", "Strip whitespace, add +1 prefix"]
}
sample_df = pd.DataFrame(sample_data)

st.download_button(
    label="📥 Download Sample STTM Template",
    data=sample_df.to_csv(index=False),
    file_name="sample_sttm.csv",
    mime="text/csv"
)

st.write("---")

uploaded_file = st.file_uploader("Upload your completed mapping schema (CSV):", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### 📋 Uploaded Mapping Schema:")
    st.dataframe(df)
    
    if st.button("🚀 Compile PySpark Code"):
        with st.spinner("Analyzing rules and compiling pipeline..."):
            time.sleep(2) # Simulates network lag
            
            # This simulates what the AI would return so you can test the UI flow
            mock_pyspark = """# Compiled PySpark Pipeline via DE Copilot
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("STTM_Pipeline").getOrCreate()

# Reading source dataframe
df_src = spark.read.table("src_users")

# Executing transformation rules mapped from STTM
df_target = df_src.select(
    F.col("user_id").alias("customer_id"),
    F.when(F.col("raw_phone").isNotNull(), 
           F.concat(F.lit("+1"), F.trim(F.col("raw_phone"))))
     .otherwise(None).alias("cleaned_phone")
)

# Writing to target dimensions table
df_target.write.mode("append").saveAsTable("dim_customers")
print("Pipeline built successfully!") """
            
            st.write("### 💻 Compiled PySpark Output (Local Mock Mode):")
            st.code(mock_pyspark, language="python")