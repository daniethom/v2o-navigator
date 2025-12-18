import streamlit as st
import pandas as pd

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator", layout="wide")
st.title("🚀 V2O Navigator: RVTools Parser")

# --- FUNCTIONS (The Brains) ---

def process_rvtools(file):
    """
    Enhanced parser to handle different RVTools versions and numeric formatting.
    """
    # Read the CSV file
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip() # Clean invisible spaces

    # mapping of what we want : what might be in the file
    mapping = {
        'VM': 'VM',
        'CPUs': 'CPUs',
        'Memory': 'Memory',
        'OS': 'OS according to the configuration file' # <--- Fixed name
    }

    # Check if these exist, if not, try to find the "closest" match
    for key, expected in mapping.items():
        if expected not in df.columns:
            # Look for any column that contains the key (e.g. "OS")
            found = [col for col in df.columns if key in col]
            if found:
                mapping[key] = found[0]
            else:
                st.error(f"Could not find a column for {key}. Please check your CSV.")
                return None

    # Filter to only the columns we need
    df = df[[mapping['VM'], mapping['CPUs'], mapping['Memory'], mapping['OS']]]

    # Rename them to standard names for our app logic
    df.columns = ['VM', 'CPUs', 'Memory', 'OS']

    # CLEAN NUMERIC DATA: Remove commas and convert to numbers
    for col in ['CPUs', 'Memory']:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)

    return df

# --- USER INTERFACE ---
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload RVTools vInfo CSV", type=["csv"])

if uploaded_file:
    data = process_rvtools(uploaded_file)

    if data is not None:
        total_vms = len(data)
        total_cpus = data['CPUs'].sum()
        total_ram_gb = data['Memory'].sum() / 1024

        st.header("📋 Infrastructure Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total VMs", total_vms)
        col2.metric("Total vCPUs", int(total_cpus))
        col3.metric("Total RAM (GB)", f"{total_ram_gb:,.0f}")

        # RHEL Detection
        rhel_vms = data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]
        num_rhel = len(rhel_vms)

        st.header("💰 RHEL Savings Potential")
        st.write(f"We found **{num_rhel}** VMs running Red Hat Enterprise Linux.")

        savings = num_rhel * 800
        st.success(f"Potential Annual RHEL License Saving: **${savings:,}**")

        with st.expander("View Cleaned Data"):
            st.dataframe(data)
