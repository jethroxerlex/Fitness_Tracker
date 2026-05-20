import streamlit as st
import bcrypt
from db.db import get_connection


def login_page():
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                con = get_connection()
                cur = con.cursor()

                cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
                user = cur.fetchone()

                if user is None:
                    st.error("Username not found.")
                    con.close()

                else:
                    stored_hash = user[6]

                    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):

                        cur.execute("""
                            SELECT age, weight, height, goal
                            FROM Users
                            WHERE user_id = ?
                        """, (user[0],))

                        profile = cur.fetchone()

                        st.session_state["user"] = {
                            "user_id": user[0],
                            "username": user[1],
                            "first_name": user[2]
                        }

                        st.success(f"Welcome back, {user[2]}!")

                        
                        if profile is None or any(field is None for field in profile):
                            st.info("Finish your profile to get the best experience!")
                            #st.button("Go to profile")
                            st.session_state.page = "profile"
                            st.rerun()
                        else:
                            st.session_state.page = "dashboard"

                        st.rerun()

                    else:
                        st.error("Incorrect password.")

                con.close()

    st.divider()

    st.write("Don't have an account?")

    if st.button("Register here"):
        st.session_state.page = "register"
        st.rerun()


def require_auth():
    if "user" not in st.session_state:
        st.warning("Please log in to access this page.")
        st.stop()