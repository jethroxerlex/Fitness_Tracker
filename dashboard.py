import streamlit as st
import anthropic
import base64
from PIL import Image
import io
from dotenv import load_dotenv
import os
import json
from datetime import date
from db.db import get_connection
from utils.helpers import calculate_age
import pandas as pd
import plotly.express as px

# API SETUP

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("API_KEY")
)

# MAIN DASHBOARD

def show_dashboard():

    # AUTH CHECK
  
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.session_state.page = "login"
        st.rerun()

    user = st.session_state["user"]

    # SIDEBAR

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

    # SESSION INIT

    if "daily_goal" not in st.session_state:
        st.session_state.daily_goal = 2000

    # GET USER PROFILE

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT username, first_name, birth_date, sex, weight, height, goal
        FROM Users
        WHERE user_id = ?
    """, (user["user_id"],))

    db_profile = cur.fetchone()
    con.close()

    if db_profile is None:
        st.error("User profile not found.")
        st.stop()

    username = db_profile[0]
    first_name = db_profile[1]
    birth_date = db_profile[2]
    sex = db_profile[3]
    weight = db_profile[4]
    height = db_profile[5]
    goal = db_profile[6]

    age = calculate_age(birth_date)
    
    # DAILY CALORIES
    
    if weight and height:

        if sex == "Male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # ACTIVITY LEVEL

        tdee = bmr * 1.55

        # GOALS

        if goal == "Lose Weight":
            daily_goal = tdee - 500

        elif goal == "Gain Muscle":
            daily_goal = tdee + 300

        else:
            daily_goal = tdee

    else:
        daily_goal = 2000                        

    # BMI CALCULATION

    if weight and height:
        height_m = float(height) / 100
        bmi = float(weight) / (height_m ** 2)
    else:
        bmi = None

    # BMI CATEGORY

    if bmi is not None:
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
    else:
        bmi_category = "N/A"

    # DASHBOARD PAGE

    if page == "Dashboard":
        
        st.title(f"Welcome, {first_name}!")

        st.divider()

        # FITNESS STATS
      
        st.subheader("📊 Your Fitness Stats")

        col1, col2, col3 = st.columns(3)

        col1.metric("Weight", f"{weight} kg")
        col2.metric("Height", f"{height} cm")
        col3.metric("BMI", f"{bmi:.1f}" if bmi else "N/A")

        st.caption(f"Category: {bmi_category}")

       
        # WEIGHT PROGRESS SECTION
       

        st.divider()

        st.subheader("📈 Weight Progress")

        # LOAD WEIGHT HISTORY

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT progress_date, progress_weight
            FROM WeightProgress
            WHERE user_id = ?
            ORDER BY progress_date ASC
        """, (user["user_id"],))

        weight_logs = cur.fetchall()

        con.close()

        # SHOW GRAPH

        if weight_logs:

            df = pd.DataFrame(
                weight_logs,
                columns=["Date", "Weight"]
            )

            fig = px.line(
                df,
                x="Date",
                y="Weight",
                markers=True,
                title="Weight Progress"
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=24,
                font=dict(size=14),
                height=450
            )

            fig.update_traces(
                line=dict(width=4),
                marker=dict(size=10)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("No weight progress yet.")

        st.divider()

        # DAILY FOOD LOGS

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT meal_type, food_name, calories, protein, carbs, fat
            FROM FoodLogs
            WHERE user_id = ? AND DATE(created_at) = DATE('now')
        """, (user["user_id"],))

        logs = cur.fetchall()
        con.close()

        total_calories = sum(row[2] or 0 for row in logs)
        total_protein = sum(row[3] or 0 for row in logs)
        total_carbs = sum(row[4] or 0 for row in logs)
        total_fat = sum(row[5] or 0 for row in logs)

        st.subheader("📊 Today's Nutrition Summary")

        # REMAINING CALORIES

        remaining_calories = daily_goal - total_calories
        
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Calories", f"{total_calories:.0f} kcal")

        st.markdown(
            f"""
            <p style='font-size:16px; color:gray; margin-top:-10px;'>
                {remaining_calories:.0f} kcal remaining
            </p>
            """,
            unsafe_allow_html=True
        )

        col2.metric("Protein", f"{total_protein:.0f} g")
        col3.metric("Carbs", f"{total_carbs:.0f} g")
        col4.metric("Fat", f"{total_fat:.0f} g")

        st.divider()

        # FOOD HISTORY

        meal_sections = ["Breakfast", "Lunch", "Dinner", "Snacks"]

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

        st.divider()

        # IMAGE UPLOAD + AI

        tab1, tab2 = st.tabs([
            "Food Analyzer",
            "Recipe Generator"
        ])

       
        # FOOD ANALYZER
        

        with tab1:

            st.markdown("### 📸 Upload Food Image")

            if "uploader_key" not in st.session_state:
                st.session_state["uploader_key"] = 0

            uploaded_file = st.file_uploader(
                "Upload your meal",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"uploaded_file{st.session_state['uploader_key']}"
            )

            if uploaded_file is not None:

                image = Image.open(uploaded_file).convert("RGB")

                st.image(
                    image,
                    caption="Uploaded Food",
                    width=300
                )

                buffer = io.BytesIO()

                image.save(
                    buffer,
                    format="JPEG"
                )

                image_base64 = base64.b64encode(
                    buffer.getvalue()
                ).decode("utf-8")

                if "ai_result" not in st.session_state:

                    prompt = f"""
                    You are a smart nutrition AI. Analyze the uploaded food image carefully.

                    User Profile:
                    - Name: {first_name}
                    - Fitness Goal: {goal}

                    Tasks:
                    1. Identify the main food items in the image.
                    2. Estimate their nutritional content for a standard serving:
                    - Calories (kcal)
                    - Protein (grams)
                    - Carbs (grams)
                    - Fat (grams)
                    3. Score the meal's healthiness (0-100) using these rules:
                    - Base score 50
                    - +20 if vegetables present
                    - +15 if lean protein present
                    - -20 if deep fried/high oil
                    - -15 if sugary food present
                    - -10 if processed food present
                    4. Suggest one personalized recommendation for the user.
                    5. Suggest a short workout based on their goal.

                    Return ONLY in **JSON format** exactly like this (no extra text, no explanations):

                    {{
                        "food_name": "",
                        "calories": 0,
                        "protein": 0,
                        "carbs": 0,
                        "fat": 0,
                        "health_score": 0,
                        "recommendation": "",
                        "workout": ""
                    }}
                    """

                with st.spinner("Analyzing food..."):

                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=500,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/jpeg",
                                            "data": image_base64
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    )

                    result = response.content[0].text

                try:

                    cleaned = (
                        result
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                    data = json.loads(cleaned)

                except Exception:

                    st.error("Error parsing AI response")
                    st.write(result)
                    st.stop()

                st.subheader("AI Result")

                col1, col2 = st.columns(2)

                with col1:

                    st.write(f" **{data['food_name']}**")
                    st.write(f" Calories: {data['calories']}")
                    st.write(f" Protein: {data['protein']}g")
                    st.write(f" Carbs: {data['carbs']}g")
                    st.write(f" Fat: {data['fat']}g")

                with col2:

                    st.write("### Health Score")

                    st.progress(
                        int(data.get("health_score", 0))
                    )

                    st.write(
                        f"{int(data.get('health_score'))} / 100"
                    )

                st.divider()

                st.write("Recommendation")
                st.write(data["recommendation"])

                st.write("Workout")
                st.write(data["workout"])

                st.info("Does this look right? Save it to your log below.")

                meal_type = st.selectbox(
                    "Meal Type",
                    ["Breakfast", "Lunch", "Dinner", "Snacks"],
                    key="food_meal_type"
)

                if st.button("✅ Save to Log"):

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
                        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    """, (
                        user["user_id"],
                        data["food_name"],
                        data["calories"],
                        data["protein"],
                        data["carbs"],
                        data["fat"],
                        meal_type
                    ))

                    con.commit()
                    con.close()

                    st.success(f"✅ {data['food_name']} saved to your log!")

                    if "ai_result" in st.session_state:
                        del st.session_state["ai_result"]

                    st.session_state["uploader_key"] += 1

                    st.rerun()

       
        # AI RECIPE GENERATOR
       

        with tab2:

            st.markdown("### AI Recipe Generator")

            # GET USER CALORIE GOAL

            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                SELECT calorie_goal
                FROM UserGoals
                WHERE user_id = ?
            """, (user["user_id"],))

            goal_data = cur.fetchone()

            daily_goal = goal_data[0] if goal_data else 2000

            # GET TODAY'S CALORIES

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


            # INGREDIENT INPUT

            recipe_ingredients = st.text_area(
                "What ingredients do you have?",
                placeholder="""
                Chicken, eggs, rice, broccoli...
                """
            )

            # GENERATE BUTTON

            if st.button("Generate Recipe"):

                recipe_prompt = f"""
                Generate a healthy fitness recipe.

                The recipe must be for ONE serving only.

                User Goal:
                {goal}

                STRICT calorie budget:
                The total recipe calories MUST NOT exceed {remaining_calories:.0f} kcal

                Available ingredients:
                {recipe_ingredients}

                Rules:
                - Prioritize the listed ingredients
                - Keep recipe realistic and easy
                - MAKE the portions for ONE SERVING ONLY!
                - Keep calories BELOW the limit
                - High protein if possible
                - Include exact measurements
                - Please MAKE THE MEASUREMENT REALISTIC FOR ONE SERVING ONLY!!

                Return ONLY valid JSON format:

                {{
                    "recipe_name": "",
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "ingredients": [
                        "",
                        ""
                    ],
                    "instructions": [
                        "",
                        ""
                    ]
                }}
                """

                with st.spinner("Generating recipe..."):

                    recipe_response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=700,
                        messages=[
                            {
                                "role": "user",
                                "content": recipe_prompt
                            }
                        ]
                    )

                    recipe_result = (
                        recipe_response
                        .content[0]
                        .text
                    )

                try:

                    cleaned_recipe = (
                        recipe_result
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                    recipe_data = json.loads(
                        cleaned_recipe
                    )

                    st.session_state["generated_recipe"] = recipe_data

                except Exception:

                    st.error("Error parsing recipe")
                    st.write(recipe_result)
                    st.stop()

                # DISPLAY RECIPE
            if "generated_recipe" in st.session_state:

                recipe_data = st.session_state["generated_recipe"]

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

                for ingredient in recipe_data["ingredients"]:
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
                    ["Breakfast", "Lunch", "Dinner", "Snacks"],
                    key="recipe_meal_type"
                )
                
                # SAVE BUTTON

                if st.button("✅ Save Recipe to Log"):

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
                        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
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
                        f"✅ {recipe_data['recipe_name']} saved!"
                    )

                    del st.session_state["generated_recipe"]

                    st.rerun()

    # PROFILE PAGE REDIRECT
   
    elif page == "Profile":

        st.session_state.page = "profile"
        st.rerun()