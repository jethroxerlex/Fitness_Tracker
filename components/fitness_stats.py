import streamlit as st

def render_fitness_stats(weight, height, bmi, bmi_category):

    st.subheader("📊 Your Fitness Stats")

    col1, col2, col3 = st.columns(3)

    col1.metric("Weight", f"{weight} kg")
    col2.metric("Height", f"{height} cm")
    col3.metric("BMI", f"{bmi:.1f}" if bmi else "N/A")

    st.caption(f"Category: {bmi_category}")