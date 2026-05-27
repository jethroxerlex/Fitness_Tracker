import streamlit as st

def render_nutrition_summary(logs, daily_goal):

    total_calories = sum(row[2] or 0 for row in logs)
    total_protein = sum(row[3] or 0 for row in logs)
    total_carbs = sum(row[4] or 0 for row in logs)
    total_fat = sum(row[5] or 0 for row in logs)

    st.subheader("📊 Today's Nutrition Summary")

    remaining_calories = daily_goal - total_calories

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Calories", f"{total_calories:.0f} kcal")
    col2.metric("Protein", f"{total_protein:.0f} g")
    col3.metric("Carbs", f"{total_carbs:.0f} g")
    col4.metric("Fat", f"{total_fat:.0f} g")