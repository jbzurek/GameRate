import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title="rankingi", layout="wide")
st.title("Rankingi gier")

# funkcja do wczytywania danych
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = Path("data/01_raw/top_500.csv")
    if not path.exists():
        st.error("nie znaleziono pliku: data/01_raw/top_500.csv")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"błąd podczas wczytywania danych: {e}")
        return pd.DataFrame()

# wczytanie danych
df = load_data()

# jeśli brak danych to nie ma co robić
if df.empty:
    st.stop()

st.success(f"wczytano dane: {len(df):,} rekordów z pliku top_500.csv")

# panel boczny z ustawieniami rankingu
st.sidebar.header("Ustawienia rankingu")

# lista kolumn numerycznych
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

if not numeric_cols:
    st.warning("brak kolumn numerycznych do utworzenia rankingu.")
    st.stop()

# próbujemy wybrać sensowną domyślną metrykę
preferred_metrics = ["pct_pos_total", "peak_ccu", "num_reviews_total", "price"]
default_metric = None
for m in preferred_metrics:
    if m in numeric_cols:
        default_metric = m
        break
if default_metric is None:
    default_metric = numeric_cols[0]

rank_by = st.sidebar.selectbox("sortuj według", numeric_cols, index=numeric_cols.index(default_metric))

# kierunek sortowania
default_ascending = False
if rank_by == "price":
    default_ascending = False  # zwykle chcemy droższe na górze w rankingu
ascending = st.sidebar.checkbox("sortuj rosnąco", value=default_ascending)

# filtr minimalnej liczby recenzji (jeśli kolumna istnieje)
min_reviews = 0
if "num_reviews_total" in df.columns and pd.api.types.is_numeric_dtype(df["num_reviews_total"]):
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filtry jakości danych**")
    max_reviews = int(df["num_reviews_total"].max())
    min_reviews = st.sidebar.slider(
        "minimalna liczba recenzji",
        min_value=0,
        max_value=max_reviews,
        value=0,
        step=max(1, max_reviews // 20),
    )

# filtr minimalnego procentu pozytywnych ocen
min_pct_pos = None
if "pct_pos_total" in df.columns and pd.api.types.is_numeric_dtype(df["pct_pos_total"]):
    min_pct_pos = st.sidebar.slider(
        "minimalny procent pozytywnych ocen",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )

# liczba gier w rankingu
top_n = st.sidebar.slider("liczba gier w rankingu", 5, 50, 10)

# kopiujemy dane do przetwarzania
rank_df = df.copy()

# zastosowanie filtra recenzji
if "num_reviews_total" in rank_df.columns and min_reviews is not None:
    rank_df = rank_df[rank_df["num_reviews_total"] >= min_reviews]

# zastosowanie filtra procentu pozytywnych ocen
if "pct_pos_total" in rank_df.columns and min_pct_pos is not None:
    rank_df = rank_df[rank_df["pct_pos_total"] >= min_pct_pos]

# wyrzucamy wiersze z nan w metryce rank_by
rank_df = rank_df[rank_df[rank_by].notna()]

# jeśli po filtrach nie ma danych
if rank_df.empty:
    st.warning("brak gier spełniających ustawione kryteria.")
    st.stop()

# sortowanie i wybór top n
rank_df = rank_df.sort_values(by=rank_by, ascending=ascending, na_position="last").head(top_n)

st.subheader(f"Top {top_n} gier według: **{rank_by}**")

# wybór kolumn do wyświetlenia
cols = []
for c in ["title", "name"]:
    if c in rank_df.columns:
        cols.append(c)

extra_cols = []
for c in ["pct_pos_total", "num_reviews_total", "price", rank_by]:
    if c in rank_df.columns and c not in cols and c not in extra_cols:
        extra_cols.append(c)

cols_to_show = cols + extra_cols
if not cols_to_show:
    cols_to_show = rank_df.columns.tolist()[:5]

# tabela z rankingiem
st.dataframe(
    rank_df[cols_to_show].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# wykres słupkowy top n gier
st.subheader("Wizualizacja rankingu")

name_col = "title" if "title" in rank_df.columns else ("name" if "name" in rank_df.columns else None)

if name_col:
    chart_df = rank_df[[name_col, rank_by]].copy()
    chart_df = chart_df.rename(columns={name_col: "game_name", rank_by: "metric"})

    bar_chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("metric:Q", title=rank_by),
            y=alt.Y("game_name:N", sort="-x", title="gra"),
            tooltip=["game_name", "metric"],
        )
        .properties(height=30 * len(chart_df))
    )
    st.altair_chart(bar_chart, use_container_width=True)
else:
    st.info("brak kolumny z nazwą gry (title/name) do podpisania wykresu.")
    st.bar_chart(rank_df[rank_by])

# dodatkowa wizualizacja: wybrana metryka vs procent pozytywnych ocen
if "pct_pos_total" in rank_df.columns and pd.api.types.is_numeric_dtype(rank_df["pct_pos_total"]):
    st.subheader("Zależność metryki od procentu pozytywnych ocen")

    scatter_df = rank_df.copy()
    if not name_col:
        scatter_df["game_name"] = scatter_df.index.astype(str)
    else:
        scatter_df["game_name"] = scatter_df[name_col]

    scatter = (
        alt.Chart(scatter_df)
        .mark_circle(size=80)
        .encode(
            x=alt.X(rank_by, title=rank_by),
            y=alt.Y("pct_pos_total", title="procent pozytywnych ocen"),
            tooltip=["game_name", rank_by, "pct_pos_total"],
        )
        .properties(height=350)
    )
    st.altair_chart(scatter, use_container_width=True)

st.caption("Ranking wygenerowany lokalnie z danych top_400.csv")
