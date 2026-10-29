import streamlit as st
import time
import urllib.request
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Advanced Network Traffic & QoS Monitor",
    layout="wide"
)

st.title("🌐 Advanced Network Traffic & QoS Monitor")
st.caption("Computer Networks Course Project (22PC1IN202) — Application Layer & Traffic Analyzer")

# Initialize session state variables
if "running" not in st.session_state:
    st.session_state.running = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "latencies" not in st.session_state:
    st.session_state.latencies = []

if "speeds" not in st.session_state:
    st.session_state.speeds = []

if "total_bytes_out" not in st.session_state:
    st.session_state.total_bytes_out = 0

if "total_bytes_in" not in st.session_state:
    st.session_state.total_bytes_in = 0

if "packets_sent" not in st.session_state:
    st.session_state.packets_sent = 0

if "packets_received" not in st.session_state:
    st.session_state.packets_received = 0

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

if st.sidebar.button("Reset Counters & History", use_container_width=True):
    st.session_state.logs = []
    st.session_state.latencies = []
    st.session_state.speeds = []
    st.session_state.total_bytes_out = 0
    st.session_state.total_bytes_in = 0
    st.session_state.packets_sent = 0
    st.session_state.packets_received = 0
    st.rerun()

st.divider()

# --- Section 1: Cumulative Network Traffic & Packet Stats (Input/Output) ---
st.subheader("📦 Cumulative Data & Packet Metrics (Input / Output)")
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    bytes_sent_kb = st.session_state.total_bytes_out / 1024
    st.metric("Total Data Sent (Output)", f"{bytes_sent_kb:.2f} KB")

with stat_col2:
    bytes_recv_kb = st.session_state.total_bytes_in / 1024
    st.metric("Total Data Received (Input)", f"{bytes_recv_kb:.2f} KB")

with stat_col3:
    st.metric("Total Packets Sent", f"{st.session_state.packets_sent:,}")

with stat_col4:
    st.metric("Total Packets Received", f"{st.session_state.packets_received:,}")

st.divider()

# --- Section 2: Real-Time Live Metrics ---
st.subheader("📊 Live Application-Layer Metrics")
metric_col1, metric_col2, metric_col3 = st.columns(3)
latency_slot = metric_col1.empty()
speed_slot = metric_col2.empty()
status_slot = metric_col3.empty()

# --- Section 3: Performance Charts with Axis Descriptions ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("##### ⏱️ Response Time (Latency)")
    st.caption("**Y-Axis:** Latency in milliseconds (ms) | **X-Axis:** Polling sequence")
    latency_chart_slot = st.empty()

with chart_col2:
    st.markdown("##### 🚀 Fetch Speed (Throughput)")
    st.caption("**Y-Axis:** Speed in KB/s | **X-Axis:** Polling sequence")
    speed_chart_slot = st.empty()

# --- Section 4: Event Log ---
st.subheader("📋 Event Log")
log_container = st.empty()

def render_logs():
    log_text = "\n".join(st.session_state.logs[-10:])
    log_container.text_area("Logs", value=log_text, height=130, disabled=True)

render_logs()

# Network Check Function simulating application request (HTTP GET)
def check_network():
    start_time = time.time()
    try:
        # Constructing outgoing request payload simulation
        user_agent = 'Mozilla/5.0 (ComputerNetworksProject/1.0)'
        req = urllib.request.Request(target_url, headers={'User-Agent': user_agent})
        
        # Estimate outgoing request size (headers + URL length)
        outgoing_size = len(target_url) + len(user_agent) + 100 
        
        with urllib.request.urlopen(req, timeout=3) as response:
            data = response.read()
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            incoming_size = len(data)
            duration = end_time - start_time
            speed_kbps = (incoming_size / duration) / 1024 if duration > 0 else 0
            
            return True, latency_ms, speed_kbps, outgoing_size, incoming_size
    except Exception:
        return False, 0.0, 0.0, 0, 0

# Active monitoring execution loop
if st.session_state.running:
    success, latency, speed, out_bytes, in_bytes = check_network()
    timestamp = datetime.now().strftime('%H:%M:%S')

    if success:
        latency_slot.metric("Response Time (Ping)", f"{latency:.1f} ms")
        speed_slot.metric("Fetch Speed", f"{speed:.2f} KB/s")
        status_slot.metric("Connection Status", "Online 🟢")
        
        # Update cumulative counters
        st.session_state.total_bytes_out += out_bytes
        st.session_state.total_bytes_in += in_bytes
        st.session_state.packets_sent += 1       # 1 HTTP GET Request Packet
        st.session_state.packets_received += 1   # 1 HTTP Response Packet
        
        st.session_state.latencies.append(latency)
        st.session_state.speeds.append(speed)
    else:
        latency_slot.metric("Response Time (Ping)", "N/A")
        speed_slot.metric("Fetch Speed", "0 KB/s")
        status_slot.metric("Connection Status", "Offline / Error 🔴")
        st.session_state.logs.append(f"[{timestamp}] Failed to reach target endpoint {target_url}.")
        
        # Count failed attempt as a sent packet attempt
        st.session_state.packets_sent += 1

    # Render native line charts
    if st.session_state.latencies:
        latency_chart_slot.line_chart(st.session_state.latencies)
        speed_chart_slot.line_chart(st.session_state.speeds)

    time.sleep(refresh_rate)
    st.rerun()
else:
    latency_slot.metric("Response Time (Ping)", "0 ms")
    speed_slot.metric("Fetch Speed", "0 KB/s")
    status_slot.metric("Connection Status", "Stopped ⏸️")
    
    if st.session_state.latencies:
        latency_chart_slot.line_chart(st.session_state.latencies)
        speed_chart_slot.line_chart(st.session_state.speeds)
