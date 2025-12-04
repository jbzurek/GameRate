import streamlit as st

st.set_page_config(page_title="o nas", layout="wide")

# tytuł strony
st.title("o projekcie gamerate")

# krótki opis sekcji
st.subheader("Kim jesteśmy")
st.markdown(
    """
    Jesteśmy grupą ćwiczeniową w ramach przedmiotu SUML na uczelni PJATK, jesteśmy młodym, dynamicznym zespołem
    i w ramach projektu pragniemy poszerzyć nasz zestaw umiejętności oraz zbudować portfolio i wejść na rynek IT.
    """
)

st.subheader("Cel projektu")
st.markdown(
    """
    Celem projektu jest stworzenie modelu predykcyjnego na podstawie zestawu danych gier znajdujących się na platformie steam, 
    który będzie przewidywał ich ocenę na podstawie różnych danych wejściowych takich jak gatunek, tagi etc.
    """
)

st.subheader("Stack technologiczny")
st.markdown(
    """
    Python - język programowania, tooling
    Jupyter notebook - env
    Streamlit - frontend
    Sqlite - baza danych
    Kaggle - źródło danych
    Pyplot, seaborn - generacja diagramów
    Pandas - przetwarzanie danych
    Scikit-learn - generacja modelu
    """
)

st.caption("© 2025 gamerate — strona 'o nas'")
