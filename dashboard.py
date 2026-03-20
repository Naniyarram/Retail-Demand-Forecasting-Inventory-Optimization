import streamlit as st
import pandas as pd
import requests
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv("app/.env", override=True)

st.set_page_config(page_title="Retail Demand Forecasting API", layout="wide")
st.title("📦 API-Driven Retail Demand Forecasting")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")
groq_api_key = os.getenv("GROQ_API_KEY", "")
client = None
if groq_api_key:
    from groq import Groq
    client = Groq(api_key=groq_api_key)

@st.cache_data
def load_historical_data():
    csv_path = "data/train.csv"
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"Store": "store_id", "Dept": "product_id", "Date": "date", "Weekly_Sales": "sales"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["store_id", "product_id", "date"])
    df = df.reset_index(drop=True)
    return df

df_hist = load_historical_data()
if df_hist.empty:
    st.error("Data file not found or empty.")
    st.stop()

st.sidebar.header("Configuration")
stores = df_hist["store_id"].unique()
selected_store = st.sidebar.selectbox("Select Store", stores)

products = df_hist[df_hist["store_id"] == selected_store]["product_id"].unique()
selected_product = st.sidebar.selectbox("Select Product", products)

# Filter, then ensure sorted by date and reset index
df_filtered = df_hist[(df_hist["store_id"] == selected_store) & (df_hist["product_id"] == selected_product)].copy()
df_filtered = df_filtered.sort_values(by="date").reset_index(drop=True)

if len(df_filtered) > 0:
    # Use last 7 weeks for visualization
    n_points = min(7, len(df_filtered))
    recent_sales = df_filtered["sales"].tolist()[-n_points:]
    dates_hist = df_filtered["date"].tolist()[-n_points:]
    
    last_date = df_filtered["date"].max()
    next_date_str = (last_date + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    next_date_obj = pd.to_datetime(next_date_str)
    
    error_std_val = df_filtered["sales"].std()
    error_std = error_std_val if not pd.isna(error_std_val) and error_std_val != 0 else 1000.0
else:
    recent_sales = []
    dates_hist = []
    next_date_str = pd.Timestamp.today().strftime("%Y-%m-%d")
    next_date_obj = pd.to_datetime(next_date_str)
    error_std = 1000.0

st.sidebar.subheader("Inventory Metrics")
lead_time_weeks = st.sidebar.number_input("Lead Time (Weeks)", min_value=1, value=2)
current_inventory = st.sidebar.number_input("Current Inventory", min_value=0.0, value=105556.0)

if st.sidebar.button("Generate Forecast & Reorder Decision"):
    payload = {
        "store_id": int(selected_store),
        "product_id": int(selected_product),
        "date": next_date_str,
        "recent_sales": [float(x) for x in recent_sales],
        "lead_time": int(lead_time_weeks),
        "service_level_z": 1.65,
        "current_inventory": float(current_inventory),
        "error_std": float(error_std)
    }
    
    with st.spinner("Calling FastAPI..."):
        try:
            res = requests.post(f"{API_URL}/reorder-decision", json=payload)
            if res.status_code != 200:
                st.error(f"API Error: {res.text}")
            else:
                data = res.json()
                
                # Unpack safely
                forecast = float(data.get('forecast', 0))
                reorder_point = float(data.get('reorder_point', 0))
                inventory_gap = float(data.get('inventory_gap', 0))
                action = data.get('action', 'OK')
                raw_woi = data.get('weeks_of_inventory')
                target_woi = data.get('target_woi', '4-6')
                utilization = float(data.get('utilization', 0.0))
                
                woi_display = f"{raw_woi:.2f} (Target: {target_woi})" if raw_woi is not None else f"N/A (Target: {target_woi})"
                gap_label = "Shortage" if inventory_gap > 0 else "Overstock" if inventory_gap < 0 else "Balanced"
                
                st.subheader(f"📊 Forecast & Inventory: Store {selected_store} | Product {selected_product}")
                
                # 2x3 Metric Grid
                col1, col2, col3 = st.columns(3)
                col1.metric("Forecast (Next Wk)", f"{forecast:,.0f}")
                col2.metric("Reorder Point", f"{reorder_point:,.0f}")
                col3.metric("Gap", f"{inventory_gap:,.0f} ({gap_label})")
                
                col4, col5, col6 = st.columns(3)
                col4.metric("Weeks of Inventory", woi_display)
                
                with col5:
                    st.metric("Utilization", f"{utilization:.1%}")
                    if utilization < 0.10:
                        st.caption("Low utilization indicates inefficient inventory usage")
                
                color_map = {
                    "CRITICAL_STOCKOUT": "darkred",
                    "CRITICAL_OVERSTOCK": "purple",
                    "REORDER": "orange",
                    "OVERSTOCK": "blue",
                    "OK": "green"
                }
                action_color = color_map.get(action, "black")
                col6.markdown(f"**Action:** <br/><span style='color:{action_color}; font-size:24px; font-weight:bold;'>{action}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Visualization + Text summary
                st.subheader("📈 Visualization & Data Summary")
                tab1, tab2 = st.tabs(["📊 Visual Chart", "📋 Data Summary Table"])

                with tab1:
                    fig, ax = plt.subplots(figsize=(10, 3))
                    if len(recent_sales) > 0:
                        ax.plot(dates_hist, recent_sales, marker="o", label="Historical (Last 7)")
                        ax.plot([dates_hist[-1], next_date_obj], [recent_sales[-1], forecast], marker="o", linestyle="--", label="Forecast", color="red")
                        fig.autofmt_xdate()
                    else:
                        ax.plot([next_date_obj], [forecast], marker="o", linestyle="--", label="Forecast", color="red")
                    
                    ax.legend()
                    ax.grid(True, linestyle="--", alpha=0.6)
                    st.pyplot(fig)

                with tab2:
                    if df_filtered is not None and not df_filtered.empty:
                        df_summary = df_filtered[["date", "sales"]].tail(7).copy()
                        df_summary["date"] = df_summary["date"].dt.strftime("%Y-%m-%d")
                        st.dataframe(df_summary, hide_index=True)
                        st.write(f"**Target Forecast for {next_date_str}:** {forecast:,.2f}")
                    else:
                        st.warning("No data available")
                        
                # AI Assistant Hardening
                if client:
                    st.subheader("🤖 AI Executive Recommendation")
                    prompt = f"""
                    You are a supply chain operations expert providing completely operationally feasible and phased recommendations.
                    
                    Data:
                    Forecast = {forecast:.2f}
                    Current Inventory = {current_inventory:.2f}
                    Target WOI = {target_woi}
                    Actual Weeks of Inventory (WOI) = {raw_woi}
                    Inventory Utilization = {utilization:.1%}
                    Action Decision = {action}
                    
                    Provide a concise set of key actions.
                    
                    Limit the response to a few important actions only.
                    Keep each action short and clear.
                    Avoid detailed explanations.
                    Avoid numbers, percentages, or timelines.
                    Do not structure as sections, phases, or reports.
                    Maintain consistent wording across all actions.
                    """
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.2
                        )
                        ai_output = response.choices[0].message.content
                        st.markdown(ai_output)
                    except Exception as llm_error:
                        st.warning(f"AI Assistant Error: {llm_error}")
                
        except requests.exceptions.RequestException as req_e:
            st.error(f"Backend Connection Error: Ensure FastAPI works. Logs: {req_e}")
        except Exception as e:
            st.error(f"Application Render Error: {e}")
