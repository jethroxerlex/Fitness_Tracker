import streamlit as st
import bcrypt
from db.db import get_connection
import datetime
import time
import sqlite3

def register_page():
    st.title("Create an Account")

    with st.form("register_form"):
        username = st.text_input("Username")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        birth_date = st.date_input("Birthdate",min_value=datetime.date(1900,1,1),max_value=datetime.date.today())
        sex = st.selectbox("Sex",["Male","Female"])
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            if not username or not password or not email:
                st.error("Username, email and password are required!")
            else:
                hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                con = get_connection()
                cur = con.cursor()
                try:
                    cur.execute("""
                        INSERT INTO Users (username, first_name, last_name, email, birth_date,sex, password)
                        VALUES (?, ?, ?, ?, ?, ?,?)
                    """, (username, first_name, last_name, email, str(birth_date),sex, hashed))
                    con.commit()
                    st.toast("Registration successful!", icon="✅")

                    st.markdown(
                        """
                        <div style="
                            padding: 25px;
                            border-radius: 15px;
                            background: linear-gradient(90deg, #00c853, #64dd17);
                            color: white;
                            font-size: 24px;
                            text-align: center;
                            font-weight: bold;
                            margin-top: 20px;
                        ">
                             SUCCESS! Account Created <br>
                            <span style="font-size:16px;">Redirecting to login...</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    time.sleep(3.5)

                    st.session_state.page = "login"
                    st.rerun()

                except sqlite3.IntegrityError as e:
                    
                    if "UNIQUE constraint failed: Users.username" in str(e):
                        st.error("Username already exist!")
                    else:
                        st.error(f"Database error: {e}")    

                except Exception as e:
                    st.error(f"Unexpected error: {e}.")
                finally:
                    con.close()


    if st.button("Return to Login page"):
        st.session_state.page = "login"
        st.rerun()                    