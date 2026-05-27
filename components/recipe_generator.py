import streamlit as st

from db.db import get_connection
from services.ai_service import generate_recipe

def render_recipe_generator(
    user,
    goal
):

    st.markdown("### FITA Recipe Generator")

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT calorie_goal
        FROM UserGoals
        WHERE user_id = ?
    """, (user["user_id"],))

    goal_data = cur.fetchone()

    daily_goal = (
        goal_data[0]
        if goal_data else 2000
    )

    cur.execute("""
        SELECT COALESCE(SUM(calories), 0)
        FROM FoodLogs
        WHERE user_id = ?
        AND DATE(created_at) = DATE('now')
    """, (user["user_id"],))

    consumed = cur.fetchone()[0]

    remaining_calories = max(
        0,
        daily_goal - consumed
    )

    con.close()

    recipe_ingredients = st.text_area(
        "What ingredients do you have?",
        placeholder="""
        Chicken, eggs, rice, broccoli...
        """
    )

    if st.button("Generate Recipe"):

        try:

            recipe_data = generate_recipe(
                goal,
                remaining_calories,
                recipe_ingredients
            )

            st.session_state[
                "generated_recipe"
            ] = recipe_data

        except Exception as e:

            st.error(
                "Error generating recipe"
            )

            st.write(e)

    if "generated_recipe" in st.session_state:

        recipe_data = st.session_state[
            "generated_recipe"
        ]

        st.success("Recipe generated!")

        st.subheader(
            recipe_data["recipe_name"]
        )

        st.write(
            f"Calories: "
            f"{recipe_data['calories']} kcal"
        )

        st.write(
            f"Protein: "
            f"{recipe_data['protein']}g"
        )

        st.write(
            f"Carbs: "
            f"{recipe_data['carbs']}g"
        )

        st.write(
            f"Fat: "
            f"{recipe_data['fat']}g"
        )

        st.write("### Ingredients")

        for ingredient in recipe_data[
            "ingredients"
        ]:
            st.write(f"- {ingredient}")

        st.write("### Instructions")

        for i, step in enumerate(
            recipe_data["instructions"],
            start=1
        ):
            st.write(f"{i}. {step}")

        st.divider()

        recipe_meal_type = st.selectbox(
            "Meal Type",
            [
                "Breakfast",
                "Lunch",
                "Dinner",
                "Snacks"
            ],
            key="recipe_meal_type"
        )

        if st.button(
            "✅ Save Recipe to Log"
        ):

            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                INSERT INTO FoodLogs
                (
                    user_id,
                    food_name,
                    calories,
                    protein,
                    carbs,
                    fat,
                    meal_type,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    datetime('now')
                )
            """, (
                user["user_id"],
                recipe_data["recipe_name"],
                float(recipe_data["calories"]),
                float(recipe_data["protein"]),
                float(recipe_data["carbs"]),
                float(recipe_data["fat"]),
                recipe_meal_type
            ))

            con.commit()
            con.close()

            st.success(
                f"✅ "
                f"{recipe_data['recipe_name']} "
                f"saved!"
            )

            del st.session_state[
                "generated_recipe"
            ]

            st.rerun()