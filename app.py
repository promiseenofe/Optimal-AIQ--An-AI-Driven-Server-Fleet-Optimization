import streamlit as st
import subprocess
import os
import json
import pandas as pd
import altair as alt
import sys
import matplotlib.pyplot as plt

# Define file paths
data_folder = 'data'
output_folder = 'output'

def run_script(script):
    try:
        result = subprocess.run([sys.executable, script], capture_output=True, text=True, check=True)
        st.success(f"✅ {script} executed successfully!")
        st.code(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error running {script}:")
        st.code(e.stdout + "\n" + e.stderr)

def load_historical_data():
    historical_path = os.path.join(output_folder, "historical_results.json")
    if os.path.exists(historical_path):
        with open(historical_path, "r") as f:
            return json.load(f)
    return []

def display_dynamic_data():
    st.subheader("📂 Dynamic Data Files")
    if os.path.exists(data_folder):
        files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
        for file in files:
            st.write(f"**{file}**")
            with open(os.path.join(data_folder, file), 'r') as f:
                data = json.load(f)
                st.json(data)
    else:
        st.warning("Data folder not found!")

def run_visual_chart():

    st.subheader("📈 Visualize Server Actions Over Time")

    file_path = "output/server_actions.json"

    if not os.path.exists(file_path):
        st.error("❌ server_actions.json file not found.")
        return

    try:
        with open(file_path, "r") as f:
            raw_data = json.load(f)

        # Filter for entries with timestamps and valid fields
        cleaned = [
            entry for entry in raw_data
            if "timestamp" in entry and all(k in entry for k in ["buy", "sell", "hold"])
        ]

        if not cleaned:
            st.warning("⚠️ No valid timestamped entries found in server_actions.json.")
            return

        df = pd.DataFrame(cleaned)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)

        # Plot with Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["timestamp"], df["buy"], label="Buy", marker='o')
        ax.plot(df["timestamp"], df["sell"], label="Sell", marker='x')
        ax.plot(df["timestamp"], df["hold"], label="Hold", marker='s')

        ax.set_title("Server Actions Over Time")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Count")
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error loading or visualizing data: {e}")

# Sidebar Navigation
st.sidebar.title("🧠 Server Fleet Optimization")
page = st.sidebar.radio("Navigate", ["Dynamic Data", "Historical Data", "Run Scripts", "Visual Charts"])

# Pages
if page == "Dynamic Data":
    st.title("📊 Dynamic Data Overview")
    display_dynamic_data()

elif page == "Historical Data":
    st.title("📁 Historical Results Summary")
    history = load_historical_data()
    if history:
        st.json(history[-3:])
    else:
        st.info("No historical data available yet.")

elif page == "Optimal-AIQ":
    st.title("⚙️ Script Runner")
    if st.button("1️⃣ Generate Dynamic Data"):
        run_script("generate_dynamic_data.py")

    if st.button("2️⃣ Run Optimization"):
        run_script("main.py")

    if st.button("3️⃣ Deeper Failure Investigation"):
        run_script("deeper_fail_investigation.py")

elif page == "Visual Charts":
    st.title("📈 Server Action Trends")
    run_visual_chart()
    
