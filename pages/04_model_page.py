import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path
import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


# funkcja do wczytywania danych
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = Path("data/02_interim/cleaned_top_500.csv")

    if not path.exists():
        st.error(f"nie znaleziono danych do oceny modelu: {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"błąd podczas wczytywania danych: {e}")
        return pd.DataFrame()

model_list = [
    ["Model klasyfikacyjny - scikit", "data/03_model/rf_classifier.pkl"],
    ["Autogluon", "data/03_model/models/LightGBM_BAG_L2_FULL/model.pkl"]
]

tab_labels = [i[0] for i in model_list]
tabs = st.tabs(tabs=tab_labels)

for i,tab in enumerate(tabs):
    with tab:
        st.set_page_config(page_title="model klasyfikacyjny", layout="wide")
        st.title("Model klasyfikacyjny – jakość gier (>70% = dobra gra)")
    
        # funkcja do wczytywania modelu
        @st.cache_resource(show_spinner=True)
        def load_model():
            model_path = Path(model_list[i][1])
            if not model_path.exists():
                st.error(f"nie znaleziono pliku modelu: {model_path}")
                return None
    
            artifact = joblib.load(model_path)

            if isinstance(artifact, dict):
                model = artifact.get("model", None)
                features = artifact.get("features", None)
            else:
                model = artifact
                features = None

            return model, features
    

    
        # wczytanie modelu
        model_artifact = load_model()
        if model_artifact is None:
            st.stop()
    
        model, feature_names = model_artifact
    
        # wczytanie danych
        df = load_data()
        if df.empty:
            st.stop()
    
        st.success(f"wczytano dane: {len(df):,} rekordów z cleaned_top_500.csv")
    
        # sprawdzenie targetu
        if "pct_pos_total" not in df.columns:
            st.error("w danych nie ma kolumny 'pct_pos_total' – nie da się odtworzyć targetu.")
            st.stop()
    
        # tworzenie kolumny binarnej target_bin
        df["target_bin"] = (df["pct_pos_total"] > 70).astype(int)
    
        # przygotowanie macierzy cech x
        if feature_names is not None:
            missing = [c for c in feature_names if c not in df.columns]
            if missing:
                st.warning(
                    "uwaga: w danych brakuje kolumn użytych przy treningu modelu:\n"
                    + ", ".join(missing)
                )
            existing_features = [c for c in feature_names if c in df.columns]
            X = df[existing_features]
        else:
            drop_cols = [c for c in ["pct_pos_total", "target_bin"] if c in df.columns]
            X = df.drop(columns=drop_cols, errors="ignore")
            X = X.select_dtypes(include=[np.number])
    
        # usunięcie wierszy z nan w x / y
        mask_valid = X.notna().all(axis=1)
        X = X[mask_valid]
        y = df.loc[mask_valid, "target_bin"]
    
        # predykcje modelu
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]
    
        # ramka danych z predykcjami
        df_valid = df.loc[mask_valid].copy()
        df_valid["predicted_good"] = y_pred
        df_valid["proba_good"] = y_proba
    
        # obliczanie metryk
        try:
            acc = accuracy_score(y, y_pred)
            prec = precision_score(y, y_pred, zero_division=0)
            rec = recall_score(y, y_pred, zero_division=0)
            f1 = f1_score(y, y_pred, zero_division=0)
            roc = roc_auc_score(y, y_proba)
        except Exception as e:
            st.error(f"nie udało się policzyć metryk: {e}")
            st.stop()
    
        # sekcja metryk modelu
        st.subheader("Metryki modelu (na całym zbiorze)")
    
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("accuracy", f"{acc:.3f}")
        m2.metric("precision", f"{prec:.3f}")
        m3.metric("recall", f"{rec:.3f}")
        m4.metric("f1-score", f"{f1:.3f}")
        m5.metric("roc-auc", f"{roc:.3f}")
    
        st.divider()
    
        # sekcja ważności cech (feature importance)
        st.subheader("Ważność cech (feature importance)")
    
        if hasattr(model, "feature_importances_"):
            if feature_names is not None:
                feat_names = [f for f in feature_names if f in X.columns]
            else:
                feat_names = list(X.columns)
    
            n_feats = min(len(model.feature_importances_), len(feat_names))
    
            fi_df = pd.DataFrame(
                {
                    "feature": feat_names[:n_feats],
                    "importance": model.feature_importances_[:n_feats],
                }
            ).sort_values("importance", ascending=False)
    
            top_k = 20
            fi_top = fi_df.head(top_k)
    
            c1, c2 = st.columns([2, 1])
    
            with c1:
                chart = (
                    alt.Chart(fi_top)
                    .mark_bar()
                    .encode(
                        x=alt.X("importance:Q", title="ważność"),
                        y=alt.Y("feature:N", sort="-x", title="cecha"),
                        tooltip=["feature", "importance"],
                    )
                    .properties(height=30 * len(fi_top))
                )
                st.altair_chart(chart, use_container_width=True)
    
            with c2:
                st.markdown("**top cech według modelu**")
                st.dataframe(
                    fi_top.reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("model nie udostępnia atrybutu feature_importances_ (brak ważności cech).")
    
        st.divider()
    
        # sekcja z predykcjami dla gier
        st.subheader("Predykcje jakości gier")
    
        st.sidebar.header("ustawienia wyświetlania predykcji")
        top_n = st.sidebar.slider("liczba gier do wyświetlenia", 5, 100, 20)
        sort_by_proba = st.sidebar.checkbox(
            "sortuj malejąco po prawdopodobieństwie dobrej gry", value=True
        )
    
        # sortowanie danych wynikowych
        if sort_by_proba and "proba_good" in df_valid.columns:
            df_view = df_valid.sort_values("proba_good", ascending=False)
        else:
            df_view = df_valid
    
        df_view = df_view.head(top_n)
    
        # wybór kolumn do pokazania
        candidate_name_cols = [c for c in ["title", "name"] if c in df_view.columns]
        base_cols = candidate_name_cols + ["pct_pos_total", "target_bin"]
        pred_cols = ["predicted_good", "proba_good"]
    
        cols_to_show = []
        for c in base_cols + pred_cols:
            if c in df_view.columns:
                cols_to_show.append(c)
    
        if not cols_to_show:
            cols_to_show = df_view.columns.tolist()[:8]
    
        st.dataframe(
            df_view[cols_to_show].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
    
        st.caption(
            "kolumna **predicted_good**: 1 = model uważa, że gra jest dobra (>70% pozytywnych), "
            "0 = model uważa, że nie. kolumna **proba_good** to prawdopodobieństwo bycia dobrą grą."
        )

