import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from groq import Groq

st.set_page_config(page_title="Retail Demand Forecasting", layout="wide")

st.title("📦 Retail Demand Forecasting & Inventory Optimization")


import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))





def generate_insight(question, avg_demand, safety_stock, reorder_point,
                     current_inventory, inventory_weeks, reorder_qty, mape):

    prompt = f"""
    You are a supply chain analyst.

    Rules:
    inventory_weeks < 1 → CRITICAL STOCKOUT
    1–2 → MODERATE RISK
    2–4 → HEALTHY
    >4 → OVERSTOCK

    Data:
    Average Weekly Demand: {avg_demand:.0f}
    Reorder Point: {reorder_point:.0f}
    Current Inventory: {current_inventory:.0f}
    Inventory Coverage Weeks: {inventory_weeks:.2f}
    Recommended Reorder Quantity: {reorder_qty:.0f}

    Question:
    {question}

    Respond with EXACTLY this format and keep it very short.

    Inventory Status:
    (one sentence)

    Root Cause:
    (one sentence)

    Recommended Action:
    (one sentence)
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

@st.cache_data
def load_data():
    df = pd.read_csv("weekly_sales.csv", parse_dates=["Date"])
    return df

weekly_ml = load_data()



features = [c for c in weekly_ml.columns if c not in ["Weekly_Sales", "Date"]]

split_date = weekly_ml["Date"].quantile(0.8)

train_ml = weekly_ml[weekly_ml["Date"] <= split_date]
test_ml  = weekly_ml[weekly_ml["Date"] > split_date]

xtrain, ytrain = train_ml[features], train_ml["Weekly_Sales"]
xtest,  ytest  = test_ml[features],  test_ml["Weekly_Sales"]


@st.cache_resource
def load_model():
    return joblib.load("../models/xgb_forecast_model.pkl")

model = load_model()

preds = model.predict(xtest)



mae = mean_absolute_error(ytest, preds)
rmse = np.sqrt(mean_squared_error(ytest, preds))
mape = np.mean(np.abs((ytest - preds) / ytest)) * 100

st.subheader("📊 Forecast Accuracy")

col1, col2, col3 = st.columns(3)

col1.metric("MAE", f"{mae:,.2f}")
col2.metric("RMSE", f"{rmse:,.2f}")
col3.metric("MAPE", f"{mape:.2f}%")

# -----------------------


forecast_series = pd.Series(preds, index=test_ml["Date"])

lead_time_weeks = 2
service_level_z = 1.65

avg_demand = forecast_series.mean()

forecast_error = ytest - preds
error_std = forecast_error.std()

safety_stock = service_level_z * error_std * np.sqrt(lead_time_weeks)

reorder_point = (avg_demand * lead_time_weeks) + safety_stock

# -----------------------
# Inventory Input
# -----------------------

current_inventory = st.number_input(
    "Current Inventory Level",
    value=100000000
)

inventory_weeks = current_inventory / avg_demand

# Coverage Display

if inventory_weeks < 0.1:
    days = inventory_weeks * 7
    st.metric("Inventory Coverage", f"{days:.2f} days")
else:
    st.metric("Inventory Coverage", f"{inventory_weeks:.2f} weeks")

# Risk Detection

if inventory_weeks < 1:
    st.error("🚨 Critical Stockout Risk")

elif inventory_weeks < 2:
    st.warning("⚠️ Moderate Stock Risk")

elif inventory_weeks <= 4:
    st.success("✅ Inventory Level Healthy")

else:
    st.warning("📦 Overstock Risk (Excess Inventory)")

# -----------------------
# Overstock Calculation
# -----------------------

max_safe_inventory = avg_demand * 4

excess_inventory = max(0, current_inventory - max_safe_inventory)

st.metric("Excess Inventory", f"{excess_inventory:,.0f}")


reorder_qty = max(0, reorder_point - current_inventory)

st.metric(
    "Recommended Reorder Quantity",
    f"{reorder_qty:,.0f}"
)

inventory_gap = current_inventory - reorder_point

st.metric("Inventory Gap", f"{inventory_gap:,.0f}")


st.subheader("📈 Demand Forecast")

fig, ax = plt.subplots(figsize=(9,3))

ax.plot(train_ml["Date"], train_ml["Weekly_Sales"], label="Train")
ax.plot(test_ml["Date"], ytest, label="Actual")
ax.plot(test_ml["Date"], preds, label="Forecast")

ax.legend()
ax.set_xlabel("Date")
ax.set_ylabel("Weekly Sales")

st.pyplot(fig)



st.subheader("📊 Inventory Optimization Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Average Weekly Demand", f"{avg_demand:,.0f}")
col2.metric("Safety Stock", f"{safety_stock:,.0f}")
col3.metric("Reorder Point", f"{reorder_point:,.0f}")


st.subheader("🧠 Replenishment Insight")

st.success(
    f"""
Maintain at least **{reorder_point:,.0f} units** of inventory.

When stock drops below this level, trigger replenishment to
achieve a **95% service level** while minimizing stock-out risk.
"""
)



st.subheader("🤖 AI Supply Chain Assistant")

question = st.text_input("Ask about demand or inventory")

if question:

    answer = generate_insight(
        question,
        avg_demand,
        safety_stock,
        reorder_point,
        current_inventory,
        inventory_weeks,
        reorder_qty,
        mape
    )

    st.write(answer)
