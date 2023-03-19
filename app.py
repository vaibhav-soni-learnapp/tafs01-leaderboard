import email
import json
from select import select
import time
from unicodedata import name
import streamlit as st
import requests
import pandas as pd
import datetime as dt
from google.oauth2 import service_account
from gsheetsdb import connect

# set page config
st.set_page_config(page_title="LearnApp", page_icon="favicon.png")

# hide streamlit branding and hamburger menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown(
    "<h3 style='text-align: center; color: black;'>LA Cohort Leaderboard</h3>",
    unsafe_allow_html=True,
)

print(st.secrets["gcp_service_account"])

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)


# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
# @st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

def create_hyperlink(row):
    if row["Google_Classroom_Status"] == "Joined":
        return "Joined"
    else:
        url = "https://forms.gle/NaX7e7YPJk9XKaKh7"
        return f'<a href="{url}" target="_blank">Not enrolled</a>'

st.write("----")

cohort_name = st.selectbox("Select the cohort", ["lotfs-01"])
st.write("")

if st.button("Generate Leaderboard"):

    sheet_url = st.secrets[f"private_gsheets_url_{cohort_name}"]
    rows = run_query(f'SELECT * FROM "{sheet_url}"')

    # Print results.
    # for row in rows:
    #     st.write(f"{row.Name} has a score of {round(row.Score)}")
            
            

            
    df = pd.DataFrame(rows)[["RANK","LOTFS_USER_ID", "LOTFS_NAME", "LOTFS_SCORE","Google_Classroom_Status"]]
    df["RANK"] = df["RANK"].astype(int) # convert the data type of the column to integer
    #df.set_index("LOTFS_USER_ID", inplace=True)
    df["Google_Classroom_Status"] = df.apply(create_hyperlink, axis=1)

    #st.dataframe(df, escape_html=False)
    st.write("")
    st.write("")
    st.subheader(f"Leaderboard for {cohort_name.upper()}")
    #st.dataframe(df)
    df = df.to_html(escape=False)
    st.write(df, unsafe_allow_html=True)
    #st.dataframe(df, unsafe_allow_html=True)
 
