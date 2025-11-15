import streamlit as st

st.set_page_config(page_title="GameRate", layout="wide")

try:
    home = st.Page("pages/01_home_page.py", title="Strona główna")
    browse = st.Page("pages/02_browse_page.py", title="Przeglądaj")
    rankings = st.Page("pages/03_rankings_page.py", title="Rankingi")
    model = st.Page("pages/04_model_page.py", title="Model")
    about = st.Page("pages/99_about_page.py", title="O nas")

    nav = st.navigation([home, browse, rankings, model, about])
    nav.run()

except Exception:
    st.title("GameRate")
    st.write("Użyj poniższych linków, aby przejść do podstron:")

    st.page_link("pages/01_home_page.py", label="Strona główna")
    st.page_link("pages/02_browse_page.py", label="Przeglądaj")
    st.page_link("pages/03_rankings_page.py", label="Rankingi")
    st.page_link("pages/04_model_page.py", label="Model")
    st.page_link("pages/99_about_page.py", label="O nas")
