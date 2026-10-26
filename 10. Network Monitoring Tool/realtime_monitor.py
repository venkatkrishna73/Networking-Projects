import streamlit as st
import time
import urllib.request

# Page configuration
st.set_page_config(page_title="Network Latency & Speed Monitor", layout="wide")
st.title("🌐 Network Latency & Speed Monitor")
st.caption("Pure Python implementation — No external dependencies required.")

# Initialize session state variables
if "running" not in st.session_state:
    st.session_state.running = False

if "logs" not in st.session_state:
    st.session_state.logs = []

# Control buttons
col_start, col_stop, _ = st.columns([1, 1, 4])

with col_start:
    if st.button("Start", type="primary"):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.logs.append("Monitoring started...")
            st.rerun()

with col_stop:
    if st.button("Stop"):
        if st.session_state.running:
            st.session_state.running = False
            st.session_state.logs.append("Monitoring stopped.")
            st.rerun()

st.divider()

# Layout for metrics display
st.subheader("Live Network Metrics")
metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    latency_slot = st.empty()

with metric_col2:
    speed_slot = st.empty()

with metric_col3:
    status_slot = st.empty()

# Layout for Event Log
st.subheader("Event Log")
log_container = st.empty()

def render_logs():
    log_text = "\n".join(st.session_state.logs[-10:])
    log_container.text_area("Logs", value=log_text, height=150, disabled=True)

render_logs()

# Function to test network ping and speed using standard library
def check_network():
    target_url = "https://www.google.com"
    start_time = time.time()
    try:
        req = urllib.request.Request(
            target_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = response.read()
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            bytes_received = len(data)
            duration = end_time - start_time
            speed_kbps = (bytes_received / duration) / 1024 if duration > 0 else 0
            
            return True, latency_ms, speed_kbps
    except Exception as e:
        return False, 0.0, 0.0

# Active monitoring loop
if st.session_state.running:
    success, latency, speed = check_network()

    if success:
        latency_slot.metric("Response Time (Ping)", f"{latency:.1f} ms")
        speed_slot.metric("Fetch Speed", f"{speed:.2f} KB/s")
        status_slot.metric("Connection Status", "Online 🟢")
    else:
        latency_slot.metric("Response Time (Ping)", "N/A")
        speed_slot.metric("Fetch Speed", "0 KB/s")
        status_slot.metric("Connection Status", "Offline / Error 🔴")
        st.session_state.logs.append("Failed to reach target endpoint.")

    time.sleep(1)
    st.rerun()
else:
    latency_slot.metric("Response Time (Ping)", "0 ms")
    speed_slot.metric("Fetch Speed", "0 KB/s")
    status_slot.metric("Connection Status", "Stopped ⏸️")
