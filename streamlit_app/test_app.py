import streamlit as st
import duckdb
import pandas as pd

# Connect to DuckDB
conn = duckdb.connect("/app/data/my_database.duckdb")  # path inside Streamlit container
df = conn.execute("SELECT * FROM test_table").df()

# Display the table
st.title("DuckDB Test Table")
st.dataframe(df)