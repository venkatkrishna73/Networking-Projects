import streamlit as st
import time
import urllib.request
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Real-Time Network Traffic & QoS Monitor",
    layout="wide"
)

st.title("🌐 Real-Time Network Traffic & QoS Monitor")
st.caption("Computer Networks Course Project (22PC1IN202) — Isolated Endpoint Traffic & Latency Tracking")

# --- Initialize Global Session States ---
if "running" not in st.session_state:
    st.session_state.running = False

if "current_target" not in st.session_state:
    st.session_state.current_target = "https://www.google.com"

# Dictionary to hold isolated data streams per endpoint
if "endpoint_data" not in st.session_state:
    st.session_state.endpoint_data = {}

# Helper function to initialize data structure for a specific endpoint
def init_endpoint(url):
    if url not in st.session_state.endpoint_data:
        st.session_state.endpoint_data[url] = {
            "latencies": [],
            "speeds": [],
            "logs": [],
            "total_bytes_out": 0,
            "total_bytes_in": 0,
            "packets_sent": 0,
            "packets_received": 0,
            "status": "Idle ⏸️"
        }

# Initialize default endpoint
init_endpoint(st.session_state.current_target)

# --- Sidebar Controls & Past Endpoint Archive ---
st.sidebar.header("⚙️ Configuration")
target_url_input = st.sidebar.text_input("Target Endpoint", value=st.session_state.current_target)

# If user changes the endpoint, switch context cleanly
if target_url_input != st.session_state.current_target:
    st.session_state.current_target = target_url_input
    init_endpoint(target_url_input)
    st.rerun()

refresh_rate = st.sidebar.slider("Refresh Interval (s)", 1, 5, 1)

st.sidebar.divider()
st.sidebar.subheader("🚀 Monitor Controls")
col_start, col_stop = st.sidebar.columns(2)

active_data = st.session_state.endpoint_data[st.session_state.current_target]

with col_start:
    if st.button("Start Monitor", type="primary", use_container_width=True):
        if not st.session_state.running:
            st.session_state.running = True
            active_data["status"] = "Online 🟢"
            active_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring started for {st.session_state.current_target}")
            st.rerun()

with col_stop:
    if st.button("Stop", use_container_width=True):
        if st.session_state.running:
            st.session_state.running = False
            active_data["status"] = "Stopped ⏸️"
            active_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring stopped.")
            st.rerun()

if st.sidebar.button("Clear Current Endpoint Data", use_container_width=True):
    st.session_state.endpoint_data[st.session_state.current_target] = {
        "latencies": [],
        "speeds": [],
        "logs": [],
        "total_bytes_out": 0,
        "total_bytes_in": 0,
        "packets_sent": 0,
        "packets_received": 0,
        "status": "Idle ⏸️"
    }
    st.rerun()

# --- Sidebar History Archive (Past Endpoints) ---
st.sidebar.divider()
st.sidebar.subheader("📂 Past Monitored Endpoints")
st.sidebar.caption("Click an endpoint to review its isolated past data:")

for endpoint in list(st.session_state.endpoint_data.keys()):
    if st.sidebar.button(f"🔗 {endpoint}", use_container_width=True):
        st.session_state.current_target = endpoint
        st.rerun()

st.divider()

# --- Active Dashboard Header ---
st.markdown(f"### 📍 Active Endpoint Context: `{st.session_state.current_target}`")

# --- Section 1: Cumulative Data & Packet Metrics (Input / Output) ---
st.subheader("📦 Cumulative Data & Packet Metrics (Input / Output)")
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    bytes_sent_kb = active_data["total_bytes_out"] / 1024
    st.metric("Total Data Sent (Output)", f"{bytes_sent_kb:.2f} KB")

with stat_col2:
    bytes_recv_kb = active_data["total_bytes_in"] / 1024
    st.metric("Total Data Received (Input)", f"{bytes_recv_kb:.2f} KB")

with stat_col3:
    st.metric("Total Packets Sent", f"{active_data['packets_sent']:,}")

with stat_col4:
    st.metric("Total Packets Received", f"{active_data['packets_received']:,}")

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
    log_text = "\n".join(active_data["logs"][-10:])
    log_container.text_area("Logs", value=log_text, height=130, disabled=True, key=f"log_{st.session_state.current_target}")

render_logs()

# Network Check Function simulating application request (HTTP GET)
def check_network(target):
    start_time = time.time()
    try:
        user_agent = 'Mozilla/5.0 (ComputerNetworksProject/1.0)'
        req = urllib.request.Request(target, headers={'User-Agent': user_agent})
        
        outgoing_size = len(target) + len(user_agent) + 100 
        
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
    success, latency, speed, out_bytes, in_bytes = check_network(st.session_state.current_target)
    timestamp = datetime.now().strftime('%H:%M:%S')

    if success:
        latency_slot.metric("Response Time (Ping)", f"{latency:.1f} ms")
        speed_slot.metric("Fetch Speed", f"{speed:.2f} KB/s")
        status_slot.metric("Connection Status", active_data["status"])
        
        # Update isolated endpoint counters
        active_data["total_bytes_out"] += out_bytes
        active_data["total_bytes_in"] += in_bytes
        active_data["packets_sent"] += 1       
        active_data["packets_received"] += 1   
        
        active_data["latencies"].append(latency)
        active_data["speeds"].append(speed)
    else:
        latency_slot.metric("Response Time (Ping)", "N/A")
        speed_slot.metric("Fetch Speed", "0 KB/s")
        status_slot.metric("Connection Status", "Offline / Error 🔴")
        active_data["logs"].append(f"[{timestamp}] Failed to reach target endpoint {st.session_state.current_target}.")
        active_data["packets_sent"] += 1

    # Render native line charts using isolated history
    if active_data["latencies"]:
        latency_chart_slot.line_chart(active_data["latencies"])
        speed_chart_slot.line_chart(active_data["speeds"])

    time.sleep(refresh_rate)
    st.rerun()
else:
    # Render static state using isolated historical data when stopped/browsing past records
    last_lat = active_data["latencies"][-1] if active_data["latencies"] else 0.0
    last_spd = active_data["speeds"][-1] if active_data["speeds"] else 0.0
    
    latency_slot.metric("Response Time (Ping)", f"{last_lat:.1f} ms")
    speed_slot.metric("Fetch Speed", f"{last_spd:.2f} KB/s")
    status_slot.metric("Connection Status", active_data["status"])
    
    if active_data["latencies"]:
        latency_chart_slot.line_chart(active_data["latencies"])
        speed_chart_slot.line_chart(active_data["speeds"])
