import streamlit as st
from auth.login import login_page
from dashboard import show_dashboard
from db.db import init_db
from auth.register import register_page
from page.profile import profile_page

init_db()

# PAGE CONFIG
st.set_page_config(
    page_title="FITA APP",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# SESSION STATE
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

if "meal_history" not in st.session_state:
    st.session_state.meal_history = []

if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 2000

if "consumed_calories" not in st.session_state:
    st.session_state.consumed_calories = 0


# NAVIGATION CONTROL

if st.session_state.user is None:

    if st.session_state.page == "register":
        register_page()

    else:
        login_page()

else:

    if st.session_state.page == "dashboard":
        show_dashboard()

    elif st.session_state.page == "profile":
        profile_page()    

    else:
        show_dashboard()