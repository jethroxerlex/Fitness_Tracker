# FITA – AI Fitness & Nutrition Tracker

FITA is a Streamlit-based fitness tracking web application that combines nutrition tracking, AI-powered food analysis, recipe generation, and fitness monitoring into a single dashboard.

Built as an MVP/portfolio project, FITA helps users:

* Track calories and macronutrients
* Monitor weight and BMI progress
* Analyze food images using AI
* Generate fitness-friendly recipes
* Organize meals by category

# Features

## Authentication

* User login system
* Session-based authentication
* Protected dashboard routes

## Dashboard

* Personalized welcome dashboard
* Daily nutrition summary
* Remaining calorie tracking
* Fitness statistics overview

## Weight & BMI Tracking

* Weight progress graph
* BMI progress graph
* BMI category indicators:

  * Underweight
  * Normal
  * Overweight
  * Obese

## Meal Logging

Users can categorize meals into:

* Breakfast
* Lunch
* Dinner
* Snacks

Each food log stores:

* Calories
* Protein
* Carbohydrates
* Fat

## AI Food Analyzer

Upload a food image and FITA will:

* Detect food items
* Estimate calories/macros
* Generate a health score
* Give personalized recommendations
* Suggest a workout

Powered by Anthropic Claude API.

## AI Recipe Generator

Generate healthy fitness recipes based on:

* Available ingredients
* User fitness goal
* Remaining calorie budget

Recipes include:

* Calories
* Macros
* Ingredients
* Instructions

## Modular Architecture

The project was refactored into:

* Components
* Services
* Database layer
* Utility helpers

For cleaner and more maintainable code.

---

# Tech Stack

## Frontend

* Streamlit
* Plotly
* Pandas

## Backend

* Python
* SQLite

## AI Integration

* Anthropic Claude API

## Other Libraries

* Pillow
* dotenv

# Project Structure
```bash
Fitness Tracker/
│
├── assets/
│
├── auth/
│   ├── __init__.py
│   ├── login.py
│   └── register.py
│
├── components/
│   ├── __init__.py
│   ├── fitness_stats.py
│   ├── food_analyzer.py
│   ├── food_history.py
│   ├── nutrition_summary.py
│   ├── recipe_generator.py
│   ├── sidebar.py
│   └── weight_progress.py
│
├── db/
│   ├── __init__.py
│   ├── db.py
│
├── page/
│   ├── __init__.py
│   └── profile.py
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py
│   └── user_service.py
│
├── utils/
│   ├── __init__.py
│   └── helpers.py
│
├── .env
├── .gitignore
├── app.py
├── dashboard.py
├── fita.db
├── requirements.txt
└── README.md
```

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/jethroxerlex/Fitness_Tracker.git
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory.

```env
API_KEY=your_anthropic_api_key
```

---

# Initialize Database

Run:

```bash
python db/db.py
```

This creates:

* Users table
* FoodLogs table
* WeightProgress table
* UserGoals table


# Run the Application

```bash
streamlit run app.py
```

# Future Improvements

Possible future features:

* Google OAuth login
* Workout planner
* Weekly nutrition analytics
* AI chatbot fitness coach
* Mobile responsive UI
* Cloud database deployment
* Social/sharing features

---

# Challenges Solved

During development, the project involved:

* Refactoring a large dashboard into modular components
* Managing Streamlit session state
* Handling AI JSON parsing reliably
* Integrating image uploads with Anthropic API
* Creating clean Plotly visualizations
* Designing a maintainable MVP architecture

---

# Learning Outcomes

This project helped strengthen skills in:

* Python development
* Streamlit application architecture
* Database design
* API integration
* Data visualization
* Software modularization
* UI/UX iteration

---

# Team Members:
- Jethro Ramos
- Kev Rosina
- Airish Christian Tabay
- Jamees Imanuel Genese
