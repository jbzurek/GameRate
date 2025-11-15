import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="GameRate", layout="wide")
st.title("GameRate")
st.caption("prototyp platformy analityki gier steam")

# funkcja do wczytywania danych z pliku
@st.cache_data(show_spinner=False)
def load_data():
    path = Path("data/02_interim/cleaned_top_500.csv")
    if not path.exists():
        st.warning("brak danych (cleaned_top_500.csv). wyświetlam tylko układ strony.")
        return pd.DataFrame()
    return pd.read_csv(path)

# wczytanie danych
df = load_data()

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("o projekcie")
    st.markdown(
        """
        gamerate analizuje dane o grach steam i przewiduje jakość gry
        na podstawie wielu cech.
        """
    )

    st.subheader("nawigacja")
    st.page_link("pages/02_browse_page.py", label="przeglądaj gry")
    st.page_link("pages/03_rankings_page.py", label="rankingi")
    st.page_link("pages/04_model_page.py", label="model predykcyjny")
    st.page_link("pages/99_about_page.py", label="o nas")

with col2:
    st.subheader("cel projektu")
    st.info(
        """
        umożliwić eksplorację danych, tworzenie rankingów
        i przewidywanie jakości gier (>70% pozytywnych ocen).
        """
    )

st.divider()

st.subheader("podstawowe statystyki danych")

# jeśli brak danych, zatrzymujemy stronę
if df.empty:
    st.stop()

# kafelki z podstawowymi metrykami
k1, k2, k3, k4 = st.columns(4)
k1.metric("liczba gier", f"{len(df):,}")
k2.metric("średnia cena", f"{df['price'].mean():.2f} usd")
k3.metric("śr. pozytywnych ocen", f"{df['pct_pos_total'].mean():.1f}%")

# liczba kolumn z gatunkami
genre_cols = [c for c in df.columns if c.startswith("genres_")]
k4.metric("unikalne gatunki", len(genre_cols))

st.divider()

# histogram ocen
st.subheader("rozkład ocen gier")

hist = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("pct_pos_total:Q", bin=alt.Bin(maxbins=25), title="procent pozytywnych ocen"),
        y=alt.Y("count()", title="liczba gier"),
    )
    .properties(height=250)
)

st.altair_chart(hist, use_container_width=True)

# top gatunków
st.subheader("najpopularniejsze gatunki")

if genre_cols:
    top_genres = df[genre_cols].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_genres)
else:
    st.info("brak kolumn gatunków po przetwarzaniu.")

st.caption("© 2025 gamerate — strona główna")
