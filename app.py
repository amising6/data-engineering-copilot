import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import pandas as pd

st.set_page_config(
    page_title="Project Intelligence Copilot",
    page_icon="🧠",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Project Intelligence Copilot")
st.subheader("From weeks of searching to answers in seconds")

st.markdown("""
Upload project artifacts such as architecture documents, onboarding guides, STTMs, runbooks, and access checklists.
Then ask project onboarding questions in plain English.
""")

uploaded_files = st.file_uploader(
    "Upload Project Documents",
    type=["txt", "pdf", "xlsx"],
    accept_multiple_files=True
)

context = ""

if uploaded_files:
    st.success(f"{len(uploaded_files)} document(s) uploaded successfully.")

    for file in uploaded_files:
        st.write(f"📄 {file.name}")

        if file.name.endswith(".txt"):
            context += file.read().decode("utf-8") + "\n\n"

        elif file.name.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    context += page_text + "\n\n"

        elif file.name.endswith(".xlsx"):
            excel = pd.ExcelFile(file)
            for sheet in excel.sheet_names:
                df = pd.read_excel(file, sheet_name=sheet)
                context += f"\nSheet: {sheet}\n"
                context += df.to_string(index=False)
                context += "\n\n"

st.divider()

question = st.text_input(
    "Ask a project onboarding question",
    placeholder="Example: What source systems are involved?"
)

if st.button("Ask Copilot"):
    if not uploaded_files:
        st.warning("Please upload project documents first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        prompt = f"""
You are Project Intelligence Copilot for enterprise data engineering onboarding.

Use only the project documentation below to answer the question.
If the answer is not available in the documents, say that clearly.

PROJECT DOCUMENTATION:
{context[:20000]}

USER QUESTION:
{question}

Answer using this format:

## Direct Answer

## Relevant Systems

## Relevant Tables / Artifacts

## Business Rules / Logic

## Recommended Next Steps
"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        st.markdown(response.choices[0].message.content)