import streamlit as st
import pandas as pd

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator", layout="wide")
st.title("🚀 V2O Navigator: RVTools Parser")

# --- FUNCTIONS (The Brains) ---

def process_rvtools(file):
    """
    This function reads the CSV and extracts the columns we need
    for an OpenShift sizing estimate.
    """
    # Read the CSV file
    df = pd.read_csv(file)

    # RVTools headers can sometimes have leading/trailing spaces, let's clean them
    df.columns = df.columns.str.strip()

    # We focus on these key columns from the 'vInfo' tab
    required_cols = ['VM', 'CPUs', 'Memory', 'OS according to the configuration']

    # Check if the file actually has the columns we need
    if not all(col in df.columns for col in required_cols):
        st.error("Missing required columns. Please ensure this is an RVTools 'vInfo' export.")
        return None

    return df[required_cols]

# --- USER INTERFACE (The Body) ---

st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload RVTools vInfo CSV", type=["csv"])

if uploaded_file:
    # 1. Parse the file
    data = process_rvtools(uploaded_file)

    if data is not None:
        # 2. Show the raw metrics
        total_vms = len(data)
        total_cpus = data['CPUs'].sum()
        total_ram_gb = data['Memory'].sum() / 1024 # Convert MB to GB

        st.header("📋 Infrastructure Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total VMs", total_vms)
        col2.metric("Total vCPUs", total_cpus)
        col3.metric("Total RAM (GB)", f"{total_ram_gb:,.0f}")

        # 3. RHEL Detection Logic
        # We look for 'Red Hat' or 'RHEL' in the OS column
        rhel_vms = data[data['OS according to the configuration'].str.contains("Red Hat|RHEL", case=False, na=False)]
        num_rhel = len(rhel_vms)

        st.header("💰 RHEL Savings Potential")
        st.write(f"We found **{num_rhel}** VMs running Red Hat Enterprise Linux.")

        # Assume $800 saving per RHEL guest when moving to OpenShift
        savings = num_rhel * 800
        st.success(f"Potential Annual RHEL License Saving: **${savings:,}**")

        # 4. Data Preview
        with st.expander("View Filtered Data"):
            st.dataframe(data)
else:
    st.info("👋 Welcome Specialist! Please upload a vInfo CSV from RVTools in the sidebar to start the analysis.")
