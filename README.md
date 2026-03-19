# Retail-Demand-Forecasting-Inventory-Optimization
Implemented weekly retail demand forecasting using XGBoost with expanding window walk-forward validation. Achieved 1.26% MAPE, demonstrating strong predictive accuracy and stability across folds. The model supports data-driven inventory planning and replenishment decisions.


# Retail Demand Forecasting & Inventory Optimization Intelligence System

## Overview

Retail inventory planning is fundamentally a **forecasting and risk management problem**.
Underestimating demand causes **stockouts and lost revenue**, while overestimating demand leads to **overstocking and increased holding costs**.

This project builds an **end-to-end demand forecasting and inventory decision system** that predicts future sales, determines optimal inventory levels, and explains supply-chain decisions through an AI assistant.

The system combines:

* Time-series forecasting models
* Feature-driven machine learning models
* Inventory optimization logic
* Explainable AI (SHAP)
* AI-assisted decision interpretation
* Containerized deployment using Docker

The final result is an **interactive decision-support tool** that helps simulate and manage retail inventory risk.

---

# Problem Statement

Retailers must answer three critical questions every week:

1. **How much demand will occur next week?**
2. **How much inventory is required to maintain service levels?**
3. **When should replenishment orders be triggered?**

This project addresses these questions by building a system that:

* Forecasts demand using historical sales patterns
* Calculates safety stock based on forecast uncertainty
* Detects inventory risks such as stockouts or overstocking
* Recommends replenishment actions

---

# System Architecture

```
Retail Sales Data
        │
        ▼
Data Cleaning & Feature Engineering
        │
        ▼
Demand Forecasting Models
(SARIMA | Prophet | XGBoost)
        │
        ▼
Model Evaluation & Walk-Forward Validation
        │
        ▼
Inventory Optimization Engine
        │
        ▼
Risk Detection
(Stockout / Overstock)
        │
        ▼
Streamlit Dashboard
        │
        ▼
LLM Decision Assistant
```

---

# Dataset

The dataset contains **historical weekly retail sales** along with store and promotional features.

Main variables include:

* Weekly Sales
* Store
* Department
* Date
* Holiday indicators
* Promotional markdown variables
* Store type

Data preprocessing included:

* Merging multiple datasets (sales, store attributes, features)
* Handling missing markdown values
* Time-series aggregation
* Feature engineering for machine learning models

---

# Feature Engineering

To capture temporal demand dynamics, multiple time-based features were created.

### Lag Features

Historical demand signals:

```
lag_1, lag_2, lag_3, lag_4
lag_12
lag_26
lag_52
```

These allow the model to learn:

* Short-term demand momentum
* Quarterly patterns
* Half-year cycles
* Yearly seasonality

### Rolling Statistics

```
rolling_mean_4
rolling_std_4
```

These capture short-term trends and volatility.

### Calendar Features

```
year
month
week
```

These allow the model to learn seasonal effects.

---

# Forecasting Models

Three different forecasting approaches were evaluated.

## SARIMA

A classical statistical model designed for seasonal time series.

Advantages:

* Captures trend and seasonality
* Strong baseline benchmark

Performance:

```
MAPE ≈ 12.7%
```

---

## Prophet

Facebook's forecasting model designed for business time series.

Advantages:

* Handles seasonal effects automatically
* Robust to missing data

Performance:

```
MAPE ≈ 2.68%
```

---

## XGBoost (Final Model)

A gradient-boosted tree model trained on engineered features.

Advantages:

* Captures nonlinear relationships
* Uses lagged demand signals
* Handles complex seasonal patterns

Performance:

```
MAE  ≈ 955,827
RMSE ≈ 1,286,090
MAPE ≈ 2.05%
```

For retail forecasting, **MAPE under 5% is considered excellent**.

---

# Model Validation

Traditional train-test splits are unreliable for time series.

Instead, **walk-forward validation** was used.

Procedure:

```
Train on past data
Predict next horizon
Expand training window
Repeat
```

Results:

```
Average MAPE ≈ 1.26%
```

This confirms the model **generalizes well to unseen future data**.

---

# Explainability (SHAP)

SHAP values were used to understand which features drive predictions.

Top contributors:

| Feature | Interpretation          |
| ------- | ----------------------- |
| lag_52  | yearly seasonal demand  |
| lag_26  | half-year demand memory |
| year    | long-term growth trend  |
| week    | seasonal position       |
| lag_1   | recent demand momentum  |

This confirms the model learns **multi-scale seasonal patterns**.

---

# Inventory Optimization Engine

The system converts demand forecasts into **inventory decisions**.

### Safety Stock

```
Safety Stock = Z × Forecast Error × √Lead Time
```

Z-score corresponds to service level.

For a **95% service level**:

```
Z = 1.65
```

---

### Reorder Point

```
Reorder Point = (Average Demand × Lead Time) + Safety Stock
```

Example system output:

```
Average Weekly Demand: 46,748,960 units
Safety Stock: 2,999,068 units
Reorder Point: 96,496,988 units
```

---

# Inventory Risk Detection

Inventory health is determined using **coverage weeks**.

```
Coverage = Current Inventory / Average Weekly Demand
```

| Coverage  | Interpretation         |
| --------- | ---------------------- |
| < 1 week  | Critical stockout risk |
| 1–2 weeks | Moderate risk          |
| 2–4 weeks | Healthy inventory      |

> 4 weeks | Overstock risk |

---

# Example Scenario

```
Current Inventory: 999,999
Average Weekly Demand: 46,748,960
Coverage: 0.15 days
```

Result:

```
Critical Stockout Risk
Recommended Reorder Quantity: 95,496,989 units
```

---

# AI Supply Chain Assistant

An LLM layer interprets the system metrics and explains decisions in natural language.

Example interaction:

User question:

```
Why is there a stockout?
```

AI explanation:

```
Inventory Status
Critical stockout risk because inventory covers only 0.15 days of demand.

Root Cause
Current inventory is far below the reorder point required to maintain a 95% service level.

Recommended Action
Immediately reorder ~95M units to restore inventory above the reorder point.
```

This allows **non-technical stakeholders to understand the system’s decisions**.

---

# Dashboard

The Streamlit dashboard displays:

* Forecast accuracy metrics
* Demand forecast visualization
* Inventory optimization metrics
* Stockout / overstock alerts
* AI decision explanations

---

# Docker Deployment

The system is fully containerized for reproducible deployment.

Build image:

```
docker build -t retail-demand-forecast .
```

Run container:

```
docker run -p 8501:8501 retail-demand-forecast
```

Access the dashboard:

```
http://localhost:8501
```

---

# Technology Stack

Programming

* Python

Machine Learning

* XGBoost
* SARIMA
* Prophet
* Scikit-Learn

Data Processing

* Pandas
* NumPy

Explainability

* SHAP

Visualization

* Matplotlib
* Streamlit

AI Integration

* Groq LLM API

Deployment

* Docker

---

# Key Takeaways

This project demonstrates:

* End-to-end machine learning pipeline design
* Time-series forecasting techniques
* Feature-based demand modeling
* Inventory optimization algorithms
* Explainable AI methods
* LLM integration for decision interpretation
* Containerized ML deployment

---



