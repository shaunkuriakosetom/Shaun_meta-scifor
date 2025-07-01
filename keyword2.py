import streamlit as st
import pandas as pd
from collections import Counter
import re

st.title("🔑 Keyword Frequency Analyzer")

# ✅ STEP 1: Upload CSV file (Streamlit version)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # ✅ STEP 2: Load the CSV
    df = pd.read_csv(uploaded_file)
    
    # Show a preview of the data
    st.subheader("Data Preview")
    st.write(df.head())
    
    # ✅ STEP 3: Combine all text into one string
    text_data = ''
    for col in df.columns:
        text_data += ' '.join(df[col].dropna().astype(str)) + ' '
    
    # ✅ STEP 4: Clean and tokenize text
    words = re.findall(r'\b\w+\b', text_data.lower())
    
    # ✅ STEP 5: Remove common stop words
    stop_words = set([
        'the', 'and', 'of', 'in', 'to', 'a', 'is', 'for', 'on', 'with', 'that', 'as',
        'are', 'at', 'this', 'from', 'by', 'an', 'be', 'or', 'it', 'not', 'was', 'which'
    ])
    filtered_words = [word for word in words if word not in stop_words]
    
    # ✅ STEP 6: Count and show top keywords
    word_freq = Counter(filtered_words)
    top_keywords = word_freq.most_common(10)
    
    # ✅ STEP 7: Display Results (Streamlit version)
    st.subheader("🔑 Top 10 Keywords Found in the CSV:")
    
    # Display as a table
    keywords_df = pd.DataFrame(top_keywords, columns=["Keyword", "Count"])
    st.dataframe(keywords_df)
    
    # Optional: Display as a bar chart
    st.bar_chart(keywords_df.set_index("Keyword"))