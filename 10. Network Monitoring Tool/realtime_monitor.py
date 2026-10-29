import streamlit as st
import time
import urllib.request
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Network Latency & Speed Monitor",
    layout="wide"
)

st.title("🌐 Network Latency & Speed Monitor")
st.caption("Pure Python implementation — No external dependencies required.")

# Initialize session state variables
if "running" not in st.session_state:
    st.session_state.running = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "latencies" not in st.session_state:
    st.session_state.latencies = []

if "speeds" not in st.session_state:
    st.session_state.speeds = []

# Sidebar Controls
st.sidebar.header("⚙️ Configuration")
target_url = st.sidebar.text_input("Target Endpoint", value="https://www.google.com")
refresh_rate = st.sidebar.slider("Refresh Interval (s)", 1, 5, 1)

st.sidebar.divider()
col_start, col_stop = st.sidebar.columns(2)

with col_start:
    if st.button("Start Monitor", type="primary", use_container_width=True):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring started...")
            st.rerun()

with col_stop:
    if st.button("Stop", use_container_width=True):
        if st.session_state.running:
            st.session_state.running = False
            st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring stopped.")
            st.rerun()

if st.sidebar.button("Clear History", use_container_width=True):
    st.session_state.logs = []
    st.session_state.latencies = []
    st.session_state.speeds = []
    st.rerun()

st.divider()

# Live Metrics Slots
st.subheader("📊 Live Network Metrics")
metric_col1, metric_col2, metric_col3 = st.columns(3)
latency_slot = metric_col1.empty()
speed_slot = metric_col2.empty()
status_slot = metric_col2.empty() # placeholder setup

# Charts Section
chart_col1, chart_col2 = st.columns(2)
latency_chart_slot = chart_col1.empty()
speed_chart_slot = chart_col2.empty()

# Event Log Section
st.subheader("📋 Event Log")
log_container = st.empty()

def render_logs():
    log_text = "\n".join(st.session_state.logs[-10:])
    log_container.text_area("Logs", value=log_text, height=130, disabled=True)

render_logs()

# Network Check Function using standard library
def check_network():
    start_time = time.time()
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = response.read()
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            bytes_received = len(data)
            duration = end_time - start_time
            speed_kbps = (bytes_received / duration) / 1024 if duration > 0 else 0
            
            return True, latency_ms, speed_kbps
    except Exception:
        return False, 0.0, 0.0

# Active monitoring execution loop
if st.session_state.running:
    success, latency, speed = check_network()
    timestamp = datetime.now().strftime('%H:%M:%S')

    if success:
        latency_slot.metric("Response Time (Ping)", f"{latency:.1f} ms")
        speed_slot.metric("Fetch Speed", f"{speed:.2f} KB/s")
        metric_col3.metric("Connection Status", "Online 🟢")
        
        st.session_state.latencies.append(latency)
        st.session_state.speeds.append(speed)
    else:
        latency_slot.metric("Response Time (Ping)", "N/A")
        speed_slot.metric("Fetch Speed", "0 KB/s")
        metric_col3.metric("Connection Status", "Offline / Error 🔴")
        st.session_state.logs.append(f"[{timestamp}] Failed to reach target endpoint.")

    # Render native line charts
    if st.session_state.latencies:
        latency_chart_slot.line_chart(st.session_state.latencies)
        speed_chart_slot.line_chart(st.session_state.speeds)

    time.sleep(refresh_rate)
    st.rerun()
else:
    latency_slot.metric("Response Time (Ping)", "0 ms")
    speed_slot.metric("Fetch Speed", "0 KB/s")
    metric_col3.metric("Connection Status", "Stopped ⏸️")
    
    if st.session_state.latencies:
        latency_chart_slot.line_chart(st.session_state.latencies)
        speed_chart_slot.line_chart(st.session_state.speeds)
