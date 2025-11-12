import streamlit as st

st.set_page_config(page_title="GameRate", layout="wide")
st.title("GameRate")
st.caption("To jest prototyp interfejsu")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("O projekcie")
    st.markdown(
        """
        To jest opis projektu.
        """
    )

    st.subheader("Nawigacja")
    st.page_link("pages/02_browse_page.py", label="Browse")
    st.page_link("pages/03_rankings_page.py", label="Rankings")
    st.page_link("pages/99_about_page.py", label="About")

with col2:
    st.subheader("Cel projektu")
    st.info("To jest cel projektu.")

st.divider()

st.subheader("Założenia projektowe")
st.markdown(
    """
    To są założenia projektowe.
    """
)

st.caption("© 2025 GameRate — strona główna (makieta UI)")
