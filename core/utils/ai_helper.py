"use client";
import os
from openai import OpenAI
from decouple import config

# Using DeepSeek via OpenAI SDK as it's OpenAI compatible
client = OpenAI(
    api_key=config('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

def categorize_transaction(reason):
    """
    Categorizes a transaction based on the reason/description.
    """
    if not reason:
        return "Other"
        
    prompt = f"Categorize this transaction based on the reason: '{reason}'. Reply with only the category name (one or two words). Common categories: Food, Transport, Rent, Entertainment, Health, Utilities, Shopping, Salary, Investment, Other."
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a financial assistant that categorizes transactions into concise categories."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0.3
        )
        return response.choices[0].message.content.strip().replace('.', '')
    except Exception as e:
        print(f"AI Categorization Error: {e}")
        return "Other"

def generate_daily_insight(total_spent, category_breakdown):
    """
    Generates a short, engaging daily summary based on spending.
    """
    if total_spent == 0:
        return "You spent 0 XAF today! That's a great step towards your savings goals. 🚀"

    breakdown_text = ", ".join([f"{k}: {v}" for k, v in category_breakdown.items()])
    prompt = f"Write a 1-sentence friendly push notification summary for someone who spent {total_spent} XAF today. Breakdown: {breakdown_text}. Be encouraging or humorous. Emoji allowed."

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a friendly financial assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI Insight Error: {e}")
        return f"You spent {total_spent:,.0f} XAF today. Keep tracking! 📝"

def get_budget_advice(spending_data):
    """
    Provides advice based on spending data and budget limits.
    """
    # To be implemented with budget integration
    pass
