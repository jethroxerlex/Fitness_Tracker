import streamlit as st
import bcrypt
from db.db import get_connection
import base64


def login_page():
    with open("assets/background.png", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
    <style>

    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .main {{
        background: rgba(0,0,0,0.65);
    }}

    div[data-testid="stForm"] {{
        background: rgba(0,0,0,0.75);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    </style>
    """, unsafe_allow_html=True)
     

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
                    stored_hash = user[7]

                    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):

                        cur.execute("""
                            SELECT weight, height, goal
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