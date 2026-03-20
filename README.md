# 🧠 Retail Demand Forecasting & Inventory Optimization System

**A production-oriented ML system that converts demand forecasts into real inventory decisions at store–product level.**

> This project was initially built as a forecasting model and later upgraded into a complete decision intelligence system.

---

## ⚡ Quick Snapshot

* 📊 Store-product level demand forecasting (~1.26% MAPE, walk-forward)
* 📦 Inventory decision engine (WOI, Reorder Point, Utilization)
* ⚠️ Risk detection (REORDER / OVERSTOCK / CRITICAL_OVERSTOCK)
* ⚡ FastAPI-based real-time inference APIs
* 📊 Streamlit dashboard (API-driven)
* 🤖 LLM-based assistant for structured business actions

---

## 🚀 Evolution: From Model → System (v1 → v2)

### 🔹 v1 — Initial Project

* Standalone ML model (SARIMA, Prophet, XGBoost)
* Focused on forecasting accuracy
* Notebook-based workflow
* Global-level predictions
* No deployment or decision layer

---

### 🔹 v2 — Production Upgrade (Current)

This project was transformed into a **production-grade system**:

* Modular architecture (`app/`, `pipeline/`, `artifacts/`)
* FastAPI backend for real-time inference
* Store–product level forecasting
* Inventory decision engine (WOI, reorder point, utilization)
* Risk classification system (REORDER / OVERSTOCK / CRITICAL)
* Batch prediction support
* LLM-based decision assistant (controlled outputs)
* Dockerized deployment
* Unit testing for APIs and services

👉 This upgrade shifts the project from:

```text
ML Model → Decision Intelligence System
```

---

## 🎯 Problem

Retail inventory decisions depend on three key questions:

1. How much demand will occur?
2. How much inventory is required?
3. When should we reorder?

Most ML projects answer only the first.

---

## 💡 Solution Approach

```text
Forecast → Inventory Metrics → Risk Detection → Action
```

---

## 🏗️ System Architecture

```
Raw Data
   ↓
Preprocessing & Feature Engineering
   ↓
Modeling (SARIMA | Prophet | XGBoost)
   ↓
Walk-Forward Validation
   ↓
Final Model (XGBoost)
   ↓
Forecast Output
   ↓
Inventory Optimization Engine
   ↓
Risk Detection
   ↓
FastAPI (Inference Layer)
   ↓
Streamlit Dashboard (Client)
   ↓
LLM Decision Assistant
```

---

## ⚙️ Core Components

### 📈 Demand Forecasting

* Model: **XGBoost**
* Validation: Walk-forward
* Performance: ~1.26% MAPE
* Granularity: Store × Product level

---

### 🧠 Feature Engineering

```
lag_1, lag_2, lag_4, lag_12, lag_26, lag_52
rolling_mean_4, rolling_std_4
year, month, week
```

---

### 📦 Inventory Optimization Engine

```
Reorder Point = Demand × Lead Time + Safety Stock
WOI = Inventory / Forecast
Utilization = Forecast / Inventory
Gap = Reorder Point - Inventory
```

---

### ⚠️ Risk Detection

| WOI Range | Condition          |
| --------- | ------------------ |
| < 1       | CRITICAL_STOCKOUT  |
| 1–4       | REORDER            |
| 4–6       | HEALTHY            |
| 6–12      | OVERSTOCK          |
| > 12      | CRITICAL_OVERSTOCK |

---

### 🤖 AI Decision Assistant

* Uses Groq LLM
* Grounded on computed metrics
* Produces structured actions
* Avoids hallucinated numbers

---

## 📊 Model Comparison

| Model   | MAPE       |
| ------- | ---------- |
| SARIMA  | ~12.7%     |
| Prophet | ~2.68%     |
| XGBoost | **~1.26%** |

---

## 📌 Example Output

```
Forecast: 1,695
Inventory: 105,556
WOI: 62.27
Action: CRITICAL_OVERSTOCK
```

---

## ⚡ API Layer

* POST /predict
* POST /reorder-decision
* POST /predict-batch

---

## 📊 Dashboard

* Forecast visualization
* Inventory metrics
* Risk alerts
* AI recommendations

---

## 🗂️ Project Structure

```
app/
├── api/
├── services/
├── schemas/
├── core/
├── main.py

pipeline/
artifacts/
tests/
dashboard.py
Dockerfile
```

---

## 🛠️ Tech Stack

* XGBoost, Scikit-learn
* SARIMA, Prophet
* FastAPI
* Streamlit
* SHAP
* Groq LLM
* Docker

---

## 🚀 What This Project Demonstrates

* End-to-end ML system design
* Feature-driven forecasting
* Inventory optimization logic
* API-based architecture
* LLM integration with control
* Transition from model → system

---

## 🏁 Final Takeaway

This project does not stop at prediction.

It answers:

> **What is happening, what is the risk, and what action should be taken.**