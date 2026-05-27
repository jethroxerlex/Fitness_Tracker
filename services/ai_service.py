import anthropic
import os
import json
import base64

from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("API_KEY")
)

def analyze_food_image(
    image_base64,
    first_name,
    goal
):

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

    cleaned = (
        result
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(cleaned)

def generate_recipe(
    goal,
    remaining_calories,
    recipe_ingredients
):

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

    cleaned_recipe = (
        recipe_result
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(
        cleaned_recipe
    )