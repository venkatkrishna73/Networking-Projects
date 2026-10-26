import streamlit as st
import psutil
import time

# Set page title and layout
st.set_page_config(page_title="Real-Time Network Monitor", layout="wide")
st.title("🌐 Real-Time Network Monitor")

# Initialize session state variables for tracking previous counters and logs
if "running" not in st.session_state:
    st.session_state.running = False

if "prev" not in st.session_state:
    st.session_state.prev = psutil.net_io_counters()

if "logs" not in st.session_state:
    st.session_state.logs = []

# Control buttons
col_start, col_stop, _ = st.columns([1, 1, 4])

with col_start:
    if st.button("Start", type="primary"):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.prev = psutil.net_io_counters()
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
st.subheader("Network Metrics")
metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    upload_speed_slot = st.empty()
    download_speed_slot = st.empty()

with metric_col2:
    total_bytes_sent_slot = st.empty()
    total_bytes_recv_slot = st.empty()

with metric_col3:
    packets_sent_slot = st.empty()
    packets_recv_slot = st.empty()

# Layout for Event Log
st.subheader("Event Log")
log_container = st.empty()

# Display current logs
def render_logs():
    log_text = "\n".join(st.session_state.logs[-10:])  # Keep last 10 logs
    log_container.text_area("Logs", value=log_text, height=150, disabled=True)

render_logs()

# Active monitoring loop using Streamlit live auto-refresh
if st.session_state.running:
    now = psutil.net_io_counters()

    # Calculate differences over the last second
    upload_bps = now.bytes_sent - st.session_state.prev.bytes_sent
    download_bps = now.bytes_recv - st.session_state.prev.bytes_recv
    packets_sent = now.packets_sent - st.session_state.prev.packets_sent
    packets_recv = now.packets_recv - st.session_state.prev.packets_recv

    # Update state baseline
    st.session_state.prev = now

    # Render metrics in real time
    upload_speed_slot.metric("Upload Speed", f"{upload_bps / 1024:.2f} KB/s")
    download_speed_slot.metric("Download Speed", f"{download_bps / 1024:.2f} KB/s")

    total_bytes_sent_slot.metric("Total Bytes Sent", f"{now.bytes_sent / (1024 * 1024):.2f} MB")
    total_bytes_recv_slot.metric("Total Bytes Received", f"{now.bytes_recv / (1024 * 1024):.2f} MB")

    packets_sent_slot.metric("Packets Sent (last 1s)", packets_sent)
    packets_recv_slot.metric("Packets Received (last 1s)", packets_recv)

    # Wait 1 second and refresh page automatically
    time.sleep(1)
    st.rerun()
else:
    # Display initial zeroes when stopped
    upload_speed_slot.metric("Upload Speed", "0 KB/s")
    download_speed_slot.metric("Download Speed", "0 KB/s")
    total_bytes_sent_slot.metric("Total Bytes Sent", "0 MB")
    total_bytes_recv_slot.metric("Total Bytes Received", "0 MB")
    packets_sent_slot.metric("Packets Sent (last 1s)", 0)
    packets_recv_slot.metric("Packets Received (last 1s)", 0)
