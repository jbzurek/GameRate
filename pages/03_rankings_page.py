import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Rankingi", layout="wide")
st.title("Rankingi gier")

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = Path("data/top_400.csv")
    if not path.exists():
        st.error("Nie znaleziono pliku: data/top_400.csv")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Błąd podczas wczytywania danych: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

st.success(f"Wczytano dane: {len(df):,} rekordów z pliku top_400.csv")

st.sidebar.header("Ustawienia rankingu")

numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if not numeric_cols:
    st.warning("Brak kolumn numerycznych do utworzenia rankingu.")
    st.stop()

rank_by = st.sidebar.selectbox("Sortuj według", numeric_cols, index=0)
top_n = st.sidebar.slider("Liczba gier w rankingu", 5, 50, 10)

ranked_df = df.sort_values(by=rank_by, ascending=False, na_position="last").head(top_n)

st.subheader(f"Top {top_n} gier według: **{rank_by}**")

cols = [c for c in ["title", "name", rank_by] if c in ranked_df.columns]
if not cols:
    cols = ranked_df.columns.tolist()[:5]

st.dataframe(ranked_df[cols].reset_index(drop=True), use_container_width=True, hide_index=True)

st.bar_chart(ranked_df.set_index(cols[0])[rank_by])

st.caption("Ranking wygenerowany lokalnie z danych top_400.csv")
