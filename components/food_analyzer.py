import streamlit as st
import base64
import io

from PIL import Image

from services.ai_service import analyze_food_image
from db.db import get_connection

def render_food_analyzer(
    user,
    first_name,
    goal
):

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

        with st.spinner("Analyzing food..."):

            data = analyze_food_image(
                image_base64,
                first_name,
                goal
            )

        st.subheader("AI Result")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**{data['food_name']}**")
            st.write(f"Calories: {data['calories']}")
            st.write(f"Protein: {data['protein']}g")
            st.write(f"Carbs: {data['carbs']}g")
            st.write(f"Fat: {data['fat']}g")

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

            st.success(
                f"✅ {data['food_name']} saved!"
            )

            st.session_state["uploader_key"] += 1

            st.rerun()