import streamlit as st
import pandas as pd

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator", layout="wide", page_icon="🚀")
st.title("🚀 V2O Navigator: VMware to OpenShift Specialist Tool")

# --- FUNCTIONS ---

def process_rvtools(file):
    """Parses RVTools vInfo CSV, cleans data, and handles formatting."""
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    mapping = {
        'VM': 'VM',
        'CPUs': 'CPUs',
        'Memory': 'Memory',
        'OS': 'OS according to the configuration file'
    }

    for key, expected in mapping.items():
        if expected not in df.columns:
            found = [col for col in df.columns if key in col]
            if found:
                mapping[key] = found[0]
            else:
                st.error(f"Could not find a column for {key}.")
                return None

    df = df[[mapping['VM'], mapping['CPUs'], mapping['Memory'], mapping['OS']]]
    df.columns = ['VM', 'CPUs', 'Memory', 'OS']

    # Clean numeric data (handle commas)
    for col in ['CPUs', 'Memory']:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)

    return df

# --- SIDEBAR: INPUTS & ASSUMPTIONS ---

with st.sidebar:
    st.header("1. Data Ingestion")
    uploaded_file = st.file_uploader("Upload RVTools vInfo CSV", type=["csv"])

    st.divider()

    st.header("2. Sizing Assumptions")
    cpu_ratio = st.slider("vCPU Consolidation Ratio", 1.0, 6.0, 3.0,
                          help="Ratio of VM vCPUs to Physical Cores.")

    node_type = st.selectbox("Worker Node Size",
                             ["Standard (16 vCPU | 64GB RAM)",
                              "Large (32 vCPU | 128GB RAM)",
                              "Extra Large (64 vCPU | 256GB RAM)"])

    st.divider()

    st.header("3. Solution Mapping")
    storage_option = st.selectbox("Storage Provider",
                                  ["OpenShift Data Foundation (ODF)", "NetApp Trident", "Portworx", "IBM Ceph"])

# --- MAIN DASHBOARD LOGIC ---

if uploaded_file:
    data = process_rvtools(uploaded_file)

    if data is not None:
        # A. Current Estate Summary
        total_vms = len(data)
        total_cpus = data['CPUs'].sum()
        total_ram_gb = data['Memory'].sum() / 1024

        st.header("📋 Current VMware Estate Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total VMs", total_vms)
        m2.metric("Total vCPUs", int(total_cpus))
        m3.metric("Total RAM (GB)", f"{total_ram_gb:,.0f}")

        # B. RHEL Savings Calculation
        rhel_vms = data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]
        num_rhel = len(rhel_vms)
        rhel_savings = num_rhel * 800 # Est. list price per guest

        st.header("💰 Financial Benefits")
        c1, c2 = st.columns(2)
        c1.metric("Detected RHEL Guests", num_rhel)
        c2.metric("Annual RHEL Savings", f"${rhel_savings:,}")
        st.caption("Note: OpenShift subscriptions include RHEL entitlements for nodes.")

        # C. Target Sizing Logic
        if "Standard" in node_type:
            node_cores, node_ram = 16, 64
        elif "Large" in node_type:
            node_cores, node_ram = 32, 128
        else:
            node_cores, node_ram = 64, 256

        req_cores = total_cpus / cpu_ratio
        nodes_by_cpu = req_cores / node_cores
        nodes_by_ram = total_ram_gb / node_ram
        final_worker_nodes = int(max(nodes_by_cpu, nodes_by_ram)) + 1

        st.header(f"🎯 Target OpenShift Cluster ({storage_option})")
        s1, s2, s3 = st.columns(3)
        s1.metric("Required Cores", f"{req_cores:.1f}")
        s2.metric("Worker Nodes (N+1)", final_worker_nodes)
        s3.metric("Target Storage", storage_option)

        # D. Edition Table
        st.divider()
        st.subheader("OpenShift Edition Comparison")
        editions = {
            "Edition": ["OVE", "OKE", "OCP", "OPP (Plus)"],
            "ACM Included?": ["No", "No", "No", "✅ Yes"],
            "Use Case": ["VM Focus", "Base K8s", "Full Dev Stack", "Enterprise Multi-Cluster"]
        }
        st.table(pd.DataFrame(editions))

        with st.expander("View Cleaned Data Source"):
            st.dataframe(data)
else:
    st.info("Please upload a vInfo CSV to begin the migration analysis.")
