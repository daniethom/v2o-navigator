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

st.header("🎯 Target OpenShift Sizing")

# 1. Sidebar Controls for Sizing
with st.sidebar:
    st.header("2. Sizing Assumptions")
    cpu_ratio = st.slider("vCPU Consolidation Ratio", 1.0, 6.0, 3.0, help="How many VM vCPUs can fit on 1 Physical Core?")
    node_type = st.selectbox("Worker Node Instance Size",
                             ["Standard (16 vCPU | 64GB RAM)",
                              "Large (32 vCPU | 128GB RAM)",
                              "Extra Large (64 vCPU | 256GB RAM)"])

# Define node capacities based on selection
if "Standard" in node_type:
    node_cores, node_ram = 16, 64
elif "Large" in node_type:
    node_cores, node_ram = 32, 128
else:
    node_cores, node_ram = 64, 256

# 2. Calculation Logic
# We calculate required cores based on the consolidation ratio
required_cores = total_cpus / cpu_ratio
# We assume RAM is 1:1 (no oversubscription for memory is safer)
required_ram = total_ram_gb

# Calculate nodes needed based on CPU vs RAM (whichever is the bottleneck)
nodes_by_cpu = required_cores / node_cores
nodes_by_ram = required_ram / node_ram
base_nodes = max(nodes_by_cpu, nodes_by_ram)

# Add N+1 for High Availability
final_worker_nodes = int(base_nodes) + 1

# 3. Display Sizing Results
col1, col2, col3 = st.columns(3)
col1.metric("Effective Cores Needed", f"{required_cores:.1f}")
col2.metric("Worker Nodes (N+1)", final_worker_nodes)
col3.metric("Total RAM Capacity", f"{final_worker_nodes * node_ram} GB")

st.info(f"💡 **Recommendation:** Deploy **{final_worker_nodes}** worker nodes + **3** control plane (master) nodes.")

# 4. OpenShift Edition Mapping
st.header("📦 OpenShift Edition Comparison")
edition_data = {
    "Edition": ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"],
    "Best For": ["VM Migration", "Basic Containers", "Full DevOps Stack", "Multi-Cluster/Security"],
    "Includes ACM?": ["No", "No", "No", "✅ Yes"],
    "Relative Cost": ["$", "$$", "$$$", "$$$$"]
}

st.table(edition_data)
        with st.expander("View Cleaned Data"):
            st.dataframe(data)
