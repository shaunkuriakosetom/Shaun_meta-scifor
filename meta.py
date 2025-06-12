import streamlit as st

# Initialize session state for tracking keywords
if 'keywords' not in st.session_state:
    st.session_state.keywords = {
        'shaun': False,
        'important': False,
        'review': False
    }

# Text input for user
user_input = st.text_area("Enter your text:")

# Check for keywords
def check_keywords(text):
    text_lower = text.lower()
    for keyword in st.session_state.keywords:
        if keyword in text_lower:
            st.session_state.keywords[keyword] = True
            st.toast(f"Keyword detected: {keyword}!", icon="⚠️")

# Button to process text
if st.button("Analyze Text"):
    check_keywords(user_input)
    
# Display keyword status
st.write("Keyword Status:")
for keyword, status in st.session_state.keywords.items():
    st.write(f"{keyword}: {'✅' if status else '❌'}")