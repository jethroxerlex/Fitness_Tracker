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

    st.sidebar.title("Navigation")

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
        SELECT username, first_name, birth_date, weight, height, goal
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
    weight = db_profile[3]
    height = db_profile[4]
    goal = db_profile[5]

    age = calculate_age(birth_date)

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

        st.divider()

        # DAILY FOOD LOGS
        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT food_name, calories, protein, carbs, fat
            FROM FoodLogs
            WHERE user_id = ? AND DATE(created_at) = DATE('now')
        """, (user["user_id"],))

        logs = cur.fetchall()
        con.close()

        total_calories = sum(row[1] or 0 for row in logs)
        total_protein = sum(row[2] or 0 for row in logs)
        total_carbs = sum(row[3] or 0 for row in logs)
        total_fat = sum(row[4] or 0 for row in logs)

        st.subheader("📊 Today's Nutrition Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Calories", f"{total_calories:.0f} kcal")
        col2.metric("Protein", f"{total_protein:.0f} g")
        col3.metric("Carbs", f"{total_carbs:.0f} g")
        col4.metric("Fat", f"{total_fat:.0f} g")

        st.divider()

        # FOOD HISTORY
        st.subheader("🍽️ Food Logged Today")

        if not logs:
            st.info("No food logged today. Upload your meal below!")
        else:
            for row in logs:
                st.write(
                    f"🍽️ **{row[0]}** — "
                    f"{row[1]:.0f} kcal | "
                    f"P: {row[2]:.0f}g | "
                    f"C: {row[3]:.0f}g | "
                    f"F: {row[4]:.0f}g"
                )

        st.divider()

        # IMAGE UPLOAD + AI
        st.subheader("📸 Upload Food Image")

        if "uploader_key" not in st.session_state:
            st.session_state["uploader_key"] = 0

        uploaded_file = st.file_uploader(
            "Upload your meal",
            type=["png", "jpg", "jpeg", "webp"],
            key = f"uploaded_file{st.session_state['uploader_key']}"
        )

        if uploaded_file is not None:

            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Food", width=300)

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

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
                    "food_name": "",           # name of the food
                    "calories": 0,             # estimated kcal
                    "protein": 0,              # grams
                    "carbs": 0,                # grams
                    "fat": 0,                  # grams
                    "health_score": 0,         # 0-100
                    "recommendation": "",      # personalized suggestion
                    "workout": ""              # short workout suggestion
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
                cleaned = result.replace("```json", "").replace("```", "").strip()
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
                st.progress(int(data.get("health_score", 0)))
                st.write(f"{int(data.get('health_score'))} / 100")

            st.divider()

            st.write("Recommendation")
            st.write(data["recommendation"])

            st.write("Workout")
            st.write(data["workout"])

            st.info("Does this look right? Save it to your log below.")

            if st.button("✅ Save to Log"):

                con = get_connection()
                cur = con.cursor()

                cur.execute("""
                    INSERT INTO FoodLogs (user_id, food_name, calories, protein, carbs, fat)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user["user_id"],
                    data["food_name"],
                    data["calories"],
                    data["protein"],
                    data["carbs"],
                    data["fat"]
                ))

                con.commit()
                con.close()

                st.success(f"✅ {data['food_name']} saved to your log!")
                

                st.session_state["uploaded_file"] = None
                if "ai_result" in st.session_state:
                    del st.session_state["ai_result"]
                st.session_state["uploader_key"] += 1
                st.rerun() 

    # PROFILE PAGE REDIRECT
   
    elif page == "Profile":
        st.session_state.page = "profile"
        st.rerun()