import streamlit as st

def render_food_history(logs):

    meal_sections = [
        "Breakfast",
        "Lunch",
        "Dinner",
        "Snacks"
    ]

    for meal in meal_sections:

        st.subheader(f"🍽️ {meal}")

        meal_logs = [
            row for row in logs
            if row[0] == meal
        ]

        if not meal_logs:

            st.caption("No meals logged.")

        else:

            for row in meal_logs:

                st.write(
                    f"**{row[1]}** — "
                    f"{row[2]:.0f} kcal | "
                    f"P: {row[3]:.0f}g | "
                    f"C: {row[4]:.0f}g | "
                    f"F: {row[5]:.0f}g"
                )