import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
from utils.helpers import calculate_age
from components.sidebar import render_sidebar
from components.fitness_stats import render_fitness_stats
from components.weight_progress import render_weight_progress
from components.nutrition_summary import render_nutrition_summary
from components.food_history import render_food_history
from components.food_analyzer import render_food_analyzer
from components.recipe_generator import render_recipe_generator
from services.user_service import (
    get_user_profile,
    get_food_logs,
    get_weight_logs
)


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

    page = render_sidebar(user)


    # GET USER PROFILE

    db_profile = get_user_profile(
        user["user_id"]
    )

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
      
        render_fitness_stats(
            weight,
            height,
            bmi,
            bmi_category
        )

        st.divider()
        # WEIGHT PROGRESS SECTION

        weight_logs = get_weight_logs(
            user["user_id"]
        )

        render_weight_progress(
            weight_logs,
            height
        )

        st.divider()

        # DAILY FOOD LOGS

        logs = get_food_logs(
            user["user_id"]
        )

        render_nutrition_summary(
            logs,
            daily_goal
        )

        st.divider()

        # FOOD HISTORY

        render_food_history(logs)

        st.divider()

        # IMAGE UPLOAD + AI

        tab1, tab2 = st.tabs([
            "Food Analyzer",
            "Recipe Generator"
        ])

       
        # FOOD ANALYZER
        
        with tab1:
            render_food_analyzer(
                user,
                first_name,
                goal
            )
       
        # AI RECIPE GENERATOR
       
        with tab2:
            render_recipe_generator(
                user,
                goal
            )
       

    # PROFILE PAGE REDIRECT
   
    elif page == "Profile":

        st.session_state.page = "profile"
        st.rerun()