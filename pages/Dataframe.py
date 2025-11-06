import streamlit as st
import pandas as pd

def getData(path):
    df = pd.DataFrame
    pd.read_csv(path)
    return df.set_index(df.columns[29])

st.write("hello df")
