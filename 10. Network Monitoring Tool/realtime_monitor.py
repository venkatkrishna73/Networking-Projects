import streamlit as st
import time
import urllib.request
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Advanced Network Performance & Interface Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌐 Advanced Network Performance & Interface Monitor")
st.caption("Computer Networks Course Project (22PC1IN202) — Live Traffic, Latency & QoS Analyzer")

# Initialize session state variables
if "running" not in st.session_state:
    st.session_state.running = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Timestamp", "Latency (ms)", "Speed (KB/s)"])

# --- Sidebar Controls & System Specs ---
st.sidebar.header("⚙️ Configuration & Controls")
target_url = st.sidebar.text_input("Target Endpoint", value="https://www.google.com")
ping_timeout = st.sidebar.slider("Timeout (seconds)", 1, 5, 3)
refresh_rate = st.sidebar.slider("Refresh Interval (s)", 1, 5, 1)

st.sidebar.divider()
st.sidebar.subheader("🚀 Project Controls")
col_start, col_stop = st.sidebar.columns(2)

with col_start:
    if st.button("Start Monitor", type="primary", use_container_width=True):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S' )}] Monitoring started targeting {target_url}")
            st.rerun()

with col_stop:
    if st.button("Stop", use_container_width=True):
        if st.session_state.running:
            st.session_state.running = False
            st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S' )}] Monitoring stopped.")
            st.rerun()

if st.sidebar.button("Clear Logs & History", use_container_width=True):
    st.session_state.logs = []
    st.session_state.history = pd.DataFrame(columns=["Timestamp", "Latency (ms)", "Speed (KB/s)"])
    st.rerun()

# --- Main Layout: Live Hardware & Network Stats ---
st.subheader("💻 Local Network Interface Statistics (NIC)")
net_io = psutil.net_io_counters()
nic_col1, nic_col2, nic_col3, nic_col4 = st.columns(4)
nic_col1.metric("Total Bytes Sent", f"{net_io.bytes_sent / (1024**2):.2f} MB")
nic_col2.metric("Total Bytes Received", f"{net_io.bytes_recv / (1024**2):.2f} MB")
nic_col3.metric("Packets Sent", f"{net_io.packets_sent:,}")
nic_col4.metric("Packets Received", f"{net_io.packets_recv:,}")

st.divider()

# --- Layout for Real-Time Metrics Display ---
st.subheader("📊 Live Application-Layer Metrics")
metric_col1, metric_col2, metric_col3 = st.columns(3)
latency_slot = metric_col1.empty()
speed_slot = metric_col2.empty()
status_slot = metric_col3.empty()

# --- Real-Time Charts Section ---
chart_col1, chart_col2 = st.columns(2)
latency_chart_slot = chart_col1.empty()
speed_chart_slot = chart_col2.empty()

# --- Event Log Section ---
st.subheader("📋 System Event Log")
log_container = st.empty()

def render_logs():
    log_text = "\n".join(st.session_state.logs[-15:])
    log_container.text_area("Live Audit Trail", value=log_text, height=130, disabled=True, key="log_area")

render_logs()

# --- Network Probe Function ---
def check_network():
    start_time = time.time()
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=ping_timeout) as response:
            data = response.read()
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            bytes_received = len(data)
            duration = end_time - start_time
            speed_kbps = (bytes_received / duration) / 1024 if duration > 0 else 0
            
            return True, latency_ms, speed_kbps
    except Exception:
        return False, 0.0, 0.0

# --- Active Monitoring Execution Loop ---
if st.session_state.running:
    success, latency, speed = check_network()
    timestamp = datetime.now().strftime('%H:%M:%S')

    if success:
        latency_slot.metric("Response Time (Ping)", f"{latency:.1f} ms", delta=f"-{(latency*0.05):.1f} ms" if latency < 100 else f"+{(latency*0.05):.1f} ms")
        speed_slot.metric("Fetch Throughput", f"{speed:.2f} KB/s")
        status_slot.metric("Connection Status", "Online 🟢")
        
        # Append to historical dataframe
        new_row = pd.DataFrame({"Timestamp": [timestamp], "Latency (ms)": [latency], "Speed (KB/s)": [speed]})
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
    else:
        latency_slot.metric("Response Time (Ping)", "N/A", delta="Timeout")
        speed_slot.metric("Fetch Throughput", "0 KB/s")
        status_slot.metric("Connection Status", "Offline / Error 🔴")
        st.session_state.logs.append(f"[{timestamp}] Warning: Connection failed to reach {target_url}")

    # Render Charts if data exists
    if not st.session_state.history.empty:
        df_plot = st.session_state.history.set_index("Timestamp")
        with latency_chart_slot.container():
            st.markdown("**Latency Trend (ms)**")
            st.line_chart(df_plot["Latency (ms)"])
        with speed_chart_slot.container():
            st.markdown("**Throughput Trend (KB/s)**")
            st.line_chart(df_plot["Speed (KB/s)"])

    time.sleep(refresh_rate)
    st.rerun()
else:
    latency_slot.metric("Response Time (Ping)", "0 ms")
    speed_slot.metric("Fetch Throughput", "0 KB/s")
    status_slot.metric("Connection Status", "Stopped ⏸️")
    
    if not st.session_state.history.empty:
        df_plot = st.session_state.history.set_index("Timestamp")
        latency_chart_slot.line_chart(df_plot["Latency (ms)"])
        speed_chart_slot.line_chart(df_plot["Speed (KB/s)"])
