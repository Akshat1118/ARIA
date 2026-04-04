import streamlit as st
import pandas as pd
import json
from agents.memory import get_collection

st.set_page_config(
    page_title="ARIA — Database Viewer",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('<h1 style="color: #0f172a; margin-bottom: 2rem;">🗄️ Backend Database Viewer</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: left; color: #64748b;'>Viewing all patient records stored in the local <strong>ChromaDB Vector Database</strong>.</p>", unsafe_allow_html=True)

try:
    collection = get_collection()
    data = collection.get()
    
    if not data or not data.get("metadatas"):
        st.info("No patient records found in the database. Run the ARIA pipeline to store data!")
    else:
        metadatas = data["metadatas"]
        ids = data["ids"]
        documents = data["documents"]

        # Parse into a DataFrame for a beautiful table view
        df_list = []
        for i, meta in enumerate(metadatas):
            row = meta.copy()
            row["Visit ID"] = ids[i]
            row["Embedded Document"] = documents[i]
            df_list.append(row)

        df = pd.DataFrame(df_list)
        
        # Sort by date descending
        if "visit_date" in df.columns:
            df = df.sort_values("visit_date", ascending=False)
            
        # Reorder columns for better readability
        cols = ["patient_id", "patient_name", "visit_date", "triage_level", "urgency_score", "diagnosis", "confidence", "symptoms", "Embedded Document", "Visit ID"]
        display_cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
        df = df[display_cols]

        st.markdown(f"### Total Records: {len(df)}")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # Raw JSON view
        with st.expander("👀 View Raw ChromaDB JSON Structure"):
            st.json(data)

except Exception as e:
    st.error(f"Failed to load database: {e}")
