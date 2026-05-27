import streamlit as st

def render_sidebar(user):

    st.sidebar.title("FITA")
    st.sidebar.write(f"Logged in as {user['first_name']}")

    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Profile"]
    )

    if st.sidebar.button("Logout"):

        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

    return page