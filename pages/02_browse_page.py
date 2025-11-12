import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Przeglądaj", layout="wide")
st.title("Przeglądaj")

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    file_path = Path("data/top_400.csv")
    if not file_path.exists():
        st.error("Nie znaleziono pliku: data/top_400.csv")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Błąd podczas wczytywania danych: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

st.success(f"Wczytano dane: {len(df):,} rekordów z pliku top_400.csv")

st.dataframe(df.head(20), use_container_width=True, hide_index=True)

st.divider()
st.subheader("Podsumowanie danych")
st.write(df.describe(include='all'))
