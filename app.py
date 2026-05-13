import streamlit as st
import pandas as pd
import os
from dashboard import show_dashboard

# PAGE CONFIG
st.set_page_config(
    page_title="FITA APP",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stButton>button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}

.stTextInput>div>div>input {
    border-radius: 10px;
}

.stNumberInput>div>div>input {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if "meal_history" not in st.session_state:
    st.session_state.meal_history = []

if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 2000

if "consumed_calories" not in st.session_state:
    st.session_state.consumed_calories = 0

# LANDING PAGE

if st.session_state.page == "landing":

    st.title("FITA APP")
    st.subheader("AI Fitness & Nutrition Coach")

    st.write("""
    Track your meals using AI.
    
    Get:
    - Calories
    - Nutrition breakdown
    - Health score
    - Personalized recommendations
    - Workout suggestions
    """)

    with st.form("user_form"):

        name = st.text_input("Name")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=18
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=1.0,
            value=60.0
        )

        height = st.number_input(
            "Height (cm)",
            min_value=1.0,
            value=170.0
        )

        goal = st.selectbox(
            "Fitness Goal",
            [
                "Lose Weight",
                "Maintain Weight",
                "Gain Muscle"
            ]
        )

        submit = st.form_submit_button("Start FITA")

        if submit:

            st.session_state.user_profile = {
                "name": name,
                "age": age,
                "weight": weight,
                "height": height,
                "goal": goal
            }

            if os.path.exists("meal_history.csv"):

                history_df = pd.read_csv(
                    "meal_history.csv"
                )

                user_history = history_df[
                    history_df["name"] == name
                ]

                st.session_state.meal_history = (
                    user_history.to_dict("records")
                )

            else:

                st.session_state.meal_history = []
            # Save user locally
            user_df = pd.DataFrame(
                [st.session_state.user_profile]
            )

            if not os.path.exists("users.csv"):
                user_df.to_csv(
                    "users.csv",
                    index=False
                )
            else:
                user_df.to_csv(
                    "users.csv",
                    mode="a",
                    header=False,
                    index=False
                )

            st.session_state.page = "dashboard"

            st.rerun()


# DASHBOARD PAGE
elif st.session_state.page == "dashboard":

    show_dashboard()