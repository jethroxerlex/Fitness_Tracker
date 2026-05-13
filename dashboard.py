import streamlit as st
import anthropic
import base64
from PIL import Image
import io
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# API KEY
load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("API_KEY")
)


# DASHBOARD 
def show_dashboard():

    if "user_profile" not in st.session_state or st.session_state.user_profile is None: 
        st.session_state.page = "landing"
        st.rerun()

    profile = st.session_state.user_profile

    st.title("FITA Dashboard")

    st.write(f"Welcome back, {profile['name']}")

    # PROFILE METRICS
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Age", profile["age"])
    col2.metric("Weight", f"{profile['weight']} kg")
    col3.metric("Height", f"{profile['height']} cm")
    col4.metric("Goal", profile["goal"])

    # BMI
    bmi = profile["weight"] / (
        (profile["height"] / 100) ** 2
    )

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    st.subheader("BMI Analysis")

    st.write(f"### BMI: {bmi:.2f}")
    st.write(f"Category: **{category}**")

    # EDIT PROFILE BUTTON
    if st.button("← Edit Profile"):

        st.session_state.page = "landing"

        st.rerun()

    st.divider()

    # FOOD IMAGE 
    uploaded_file = st.file_uploader(
        "Upload your food image",
        type=["png", "jpg", "jpeg", "webp"]
    )

    # IMAGE ANALYSIS
    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        st.image(
            image,
            caption="Uploaded Food",
            use_container_width=300
        )

        # Convert image to JPEG
        buffer = io.BytesIO()

        image.save(buffer, format="JPEG")

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        # PROMPT
        prompt = f"""
        Analyze this food image. Assume 1 standard serving size.

        User Profile:
        - Name: {profile['name']}
        - Age: {profile['age']}
        - Weight: {profile['weight']} kg
        - Height: {profile['height']} cm
        - Fitness Goal: {profile['goal']}

        Health scoring rules:
        - Base score starts at 50
        - Add +20 if vegetables are present
        - Add +15 if lean protein is present
        - Subtract -20 if deep fried or high oil
        - Subtract -15 if sugary food is present
        - Subtract -10 if processed food is present
        - Maximum score = 100
        - Minimum score = 0

        Also suggest a daily calorie target based on:
        - age
        - weight
        - height
        - fitness goal

        Return ONLY valid JSON:

        Return ONLY a number for "calorie_target".

        {{
            "foods": [],
            "calories": 0,
            "protein": "",
            "carbs": "",
            "fat": "",
            "health_score": 0,
            "recommendation": "",
            "workout": "",
            "calorie_target": 0
        }}
        """

        # ANALYSIS
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

        # JSON PARSING
        try:

            cleaned_result = result.strip()

            cleaned_result = cleaned_result.replace("```json", "")
            cleaned_result = cleaned_result.replace("```", "")

            data = json.loads(cleaned_result)

            st.subheader("FITA AI COACH")

            # RESULTS
            col1, col2 = st.columns(2)

            with col1:

                st.write("### Foods Detected")

                for food in data["foods"]:
                    st.write(f"- {food}")

                st.write("### Calories")
                st.write(f"{data['calories']} kcal")

                st.write("### Protein")
                st.write(data["protein"])

            with col2:

                st.write("### Carbs")
                st.write(data["carbs"])

                st.write("### Fat")
                st.write(data["fat"])

                st.write("### Health Score")

                st.progress(
                    int(data["health_score"])
                )

                st.write(
                    f"{data['health_score']}"
                )

            st.divider()

            # RECOMMENDATIONS
            st.subheader("Personalized Recommendation")

            st.write(data["recommendation"])

            st.subheader("Suggested Workout")

            st.write(data["workout"])

            # DAILY GOAL
            target = int(data.get("calorie_target", 2000))

            target = max(1200, min(3500, target))

            st.session_state.daily_goal = target

            # CALORIES
            calories = int(data["calories"])

            st.session_state.consumed_calories += calories

            remaining = (
                st.session_state.daily_goal
                - st.session_state.consumed_calories
            )

            # SAVE HISTORY
            meal_data = {
                "name": profile["name"],
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "foods": ", ".join(data["foods"]),
                "calories": calories,
                "health_score": data["health_score"],
                "remaining": remaining
            }

            meal_df = pd.DataFrame([meal_data])

            if not os.path.exists("meal_history.csv"):

                meal_df.to_csv(
                    "meal_history.csv",
                    index=False
                )

            else:

                meal_df.to_csv(
                    "meal_history.csv",
                    mode="a",
                    header=False,
                    index=False
                )

            st.session_state.meal_history.append(
                meal_data
            )

        except Exception as e:

            st.error("Error parsing AI response")

            st.write(result)

    st.divider()

    # MEAL HISTORY
    st.subheader("Meal History")

    profile = st.session_state.user_profile

    if os.path.exists("meal_history.csv"):

        history_df = pd.read_csv("meal_history.csv")

        user_history = history_df[
            history_df["name"] == profile["name"]
        ]

        if not user_history.empty:

            st.dataframe(
                user_history,
                use_container_width=True
            )

        else:
            st.info("No meal history yet.")

    else:
        st.info("No meal history found.")

     # DAILY CALORIE BUDGET
    remaining = (
        st.session_state.daily_goal
        - st.session_state.consumed_calories
    )

    st.subheader("🔥 Daily Calorie Budget")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Goal",
        f"{st.session_state.daily_goal} kcal"
    )

    col2.metric(
        "Consumed",
        f"{st.session_state.consumed_calories} kcal"
    )

    col3.metric(
        "Remaining",
        f"{remaining} kcal"
    )

    # STATUS ALERTS
    if remaining > 500:
        st.success("You're on track")

    elif remaining > 0:
        st.warning("You're getting close")

    else:
        st.error("Calorie limit exceeded")

    # RESET BUTTON
    if st.button("Reset Day"):

        st.session_state.consumed_calories = 0
        st.session_state.meal_history = []

        st.success("New day started!")   