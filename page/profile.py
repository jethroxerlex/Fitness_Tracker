import streamlit as st
from db.db import get_connection
import time

def profile_page():

    # AUTH CHECK
  
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.session_state.page = "login"
        st.rerun()

    user = st.session_state["user"]

    # Sidebar
    st.sidebar.title("Navigation")

    selected_page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Profile"],
        index=1 
    )
    if selected_page == "Dashboard":
        st.session_state.page = "dashboard"
        st.rerun()

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

    # GET CURRENT DATA

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT weight, height, goal
        FROM Users
        WHERE user_id = ?
    """, (user["user_id"],))

    data = cur.fetchone()
    con.close()

    if data is None:
        st.error("Profile not found")
        st.stop()

    weight, height, goal = data
    goals = ["Lose Weight", "Maintain Weight", "Gain Muscle"]
    goal_index = goals.index(goal) if goal in goals else 0

    # FORM

    st.title(f"{user['first_name']}'s Profile")
    with st.form("edit_profile"):
        new_weight = st.number_input("Weight (kg)", value=float(weight or 70))
        new_height = st.number_input("Height (cm)", value=float(height or 170))
        new_goal = st.selectbox("Goal", goals, index=goal_index)

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                UPDATE Users
                SET weight = ?,
                    height = ?,
                    goal = ?
                WHERE user_id = ?
            """, (
                new_weight,
                new_height,
                new_goal,
                user["user_id"]
            ))

             # WEIGHT HISTORY
            cur.execute("""
                INSERT INTO WeightProgress
                (
                    user_id,
                    progress_date,
                    progress_weight
                )
                VALUES (?, DATE('now'), ?)
            """, (
                user["user_id"],
                new_weight
            ))
            con.commit()
            con.close()

            st.success("Profile updated successfully!")
            time.sleep(2.5)

            st.session_state.page = "dashboard"
            st.rerun()