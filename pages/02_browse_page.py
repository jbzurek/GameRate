import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="przeglądaj", layout="wide")
st.title("przeglądaj gry")

# funkcja do wczytywania danych
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    file_path = Path("data/01_raw/top_500.csv")
    if not file_path.exists():
        st.error("nie znaleziono pliku: data/01_raw/top_500.csv")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"błąd podczas wczytywania danych: {e}")
        return pd.DataFrame()

# wczytanie danych
df = load_data()

# jeśli brak danych to zatrzymujemy stronę
if df.empty:
    st.stop()

st.success(f"wczytano dane: {len(df):,} rekordów z pliku top_500.csv")

# panel boczny z filtrami
st.sidebar.header("filtry")

# filtr po nazwie gry
name_col = "name" if "name" in df.columns else None
search_text = st.sidebar.text_input("wyszukaj po nazwie", "")

# filtr po cenie jeśli jest kolumna price
if "price" in df.columns and pd.api.types.is_numeric_dtype(df["price"]):
    min_price = float(df["price"].min())
    max_price = float(df["price"].max())
    price_range = st.sidebar.slider(
        "zakres ceny",
        min_value=round(min_price, 2),
        max_value=round(max_price, 2),
        value=(round(min_price, 2), round(max_price, 2)),
    )
else:
    price_range = None

# wybór kolumny do sortowania
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
default_sort_col = "pct_pos_total" if "pct_pos_total" in numeric_cols else numeric_cols[0]
sort_by = st.sidebar.selectbox("sortuj według kolumny", numeric_cols, index=numeric_cols.index(default_sort_col))
ascending = st.sidebar.checkbox("sortuj rosnąco", value=False)

# zastosowanie filtrów
filtered_df = df.copy()

# filtr nazwy
if name_col and search_text.strip():
    filtered_df = filtered_df[
        filtered_df[name_col].str.contains(search_text.strip(), case=False, na=False)
    ]

# filtr ceny
if price_range and "price" in filtered_df.columns:
    low, high = price_range
    filtered_df = filtered_df[
        (filtered_df["price"] >= low) & (filtered_df["price"] <= high)
    ]

# sortowanie
if sort_by in filtered_df.columns:
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

# liczba wierszy do pokazania
top_n = st.sidebar.slider("liczba gier do wyświetlenia w tabeli", 10, 100, 30)

st.subheader("przegląd danych (filtrowalne)")
cols_to_show = []

for c in ["name", "title", "price", "pct_pos_total", "num_reviews_total"]:
    if c in filtered_df.columns:
        cols_to_show.append(c)

if not cols_to_show:
    cols_to_show = filtered_df.columns.tolist()[:8]

st.dataframe(
    filtered_df[cols_to_show].head(top_n).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("podstawowe wizualizacje")

# układ dwóch kolumn na wykresy
c1, c2 = st.columns(2)

# histogram ceny
if "price" in filtered_df.columns and pd.api.types.is_numeric_dtype(filtered_df["price"]):
    with c1:
        st.markdown("**rozkład ceny gier**")
        price_chart = (
            alt.Chart(filtered_df)
            .mark_bar()
            .encode(
                x=alt.X("price:Q", bin=alt.Bin(maxbins=30), title="cena"),
                y=alt.Y("count()", title="liczba gier"),
            )
            .properties(height=250)
        )
        st.altair_chart(price_chart, use_container_width=True)

# rozkład procenta pozytywnych ocen
if "pct_pos_total" in filtered_df.columns and pd.api.types.is_numeric_dtype(filtered_df["pct_pos_total"]):
    with c2:
        st.markdown("**rozkład pozytywnych ocen**")
        score_chart = (
            alt.Chart(filtered_df)
            .mark_bar()
            .encode(
                x=alt.X("pct_pos_total:Q", bin=alt.Bin(maxbins=30), title="procent pozytywnych ocen"),
                y=alt.Y("count()", title="liczba gier"),
            )
            .properties(height=250)
        )
        st.altair_chart(score_chart, use_container_width=True)

# liczba gier w czasie jeśli jest data wydania
if "release_date" in df.columns:
    st.markdown("**liczba gier wydanych w kolejnych latach**")
    tmp = filtered_df.copy()
    tmp["release_year"] = pd.to_datetime(tmp["release_date"], errors="coerce").dt.year
    year_counts = (
        tmp.dropna(subset=["release_year"])
        .groupby("release_year")
        .size()
        .reset_index(name="count")
    )

    if not year_counts.empty:
        year_chart = (
            alt.Chart(year_counts)
            .mark_bar()
            .encode(
                x=alt.X("release_year:O", title="rok wydania"),
                y=alt.Y("count:Q", title="liczba gier"),
            )
            .properties(height=280)
        )
        st.altair_chart(year_chart, use_container_width=True)
    else:
        st.info("brak poprawnych dat wydania do pokazania wykresu.")

st.caption("dane pochodzą z pliku top_400.csv (surowy zbiór gier)")
