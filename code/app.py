import streamlit as st
import pipeline

st.set_page_config(page_title="Data Analyst Copilot", layout="wide")

st.title("Data Analyst Copilot")
st.caption("Ask a question about the Sales data in English or Arabic.")

question = st.text_input("Your question", placeholder="What is the total cost for each country?")

if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Planning, writing code, and running it..."):
        r = pipeline.answer(question.strip())

    if r["error"]:
        st.error(f"The generated code failed: {r['error']}")
    elif "CANNOT ANSWER" in r["output"]:
        st.warning(r["output"])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Result")
        if r["output"]:
            st.code(r["output"], language=None)
        for fig in r["figures"]:
            st.pyplot(fig)

    with col2:
        st.subheader("Pandas code")
        st.code(r["code"], language="python")

    with st.expander("Plan (what the translator understood)"):
        st.text(r["plan"])

    with st.expander(f"Retrieved documentation ({r['chunk_count']} chunks)"):
        for chunk in r["chunks"]:
            st.text(chunk)
            st.divider()