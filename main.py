import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- INITIAL SETUP & THEMING ---
st.set_page_config(
    page_title="V2O Navigator | VMware to OpenShift",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS to align with Red Hat branding
st.markdown("""
    <style>
    .main { background-color: #f0f0f0; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #EE0000; }
    </style>
    """, unsafe_allow_none=True)

# --- HELPER FUNCTIONS ---

def process_rvtools(file):
    """Parses RVTools vInfo CSV, cleans headers, and handles numeric formatting."""
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        # Resilient mapping for different RVTools versions
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
                    st.error(f"Required column '{key}' not found. Please check CSV headers.")
                    return None

        # Extract and Rename
        df = df[[mapping['VM'], mapping['CPUs'], mapping['Memory'], mapping['OS']]]
        df.columns = ['VM', 'CPUs', 'Memory', 'OS']

        # Clean numeric data: Remove commas and convert to float
        for col in ['CPUs', 'Memory']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)

        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# --- SIDEBAR: CONFIGURATION ---

with st.sidebar:
    st.image("https://www.redhat.com/cms/managed-files/Logo-RedHat-OpenShift-A-Standard-RGB.png", width=200)
    st.title("V2O Navigator")

    st.header("1. Data Ingestion")
    uploaded_file = st.file_uploader("Upload RVTools vInfo CSV", type=["csv"])

    st.divider()

    st.header("2. Sizing Assumptions")
    cpu_ratio = st.slider("vCPU Consolidation Ratio", 1.0, 6.0, 3.0,
                          help="Number of VM vCPUs per Physical Core.")

    node_type = st.selectbox("Worker Node Size",
                             ["Standard (16 vCPU | 64GB RAM)",
                              "Large (32 vCPU | 128GB RAM)",
                              "Extra Large (64 vCPU | 256GB RAM)"])

    st.divider()

    st.header("3. Solution & Finance")
    storage_option = st.selectbox("Storage Solution", ["ODF (Native)", "NetApp Trident", "Portworx", "IBM Ceph"])
    edition = st.selectbox("OpenShift Edition", ["OVE (Virtualization)", "OKE (Engine)", "OCP (Platform)", "OPP (Platform Plus)"])

    annual_vmware_cost = st.number_input("Current Annual VMware Spend ($)", value=100000, step=1000)
    fte_rate = st.number_input("FTE Hourly Rate ($)", value=80)

# --- MAIN DASHBOARD ---

if uploaded_file:
    data = process_rvtools(uploaded_file)

    if data is not None:
        # A. Summary Metrics
        total_vms = len(data)
        total_cpus = data['CPUs'].sum()
        total_ram_gb = data['Memory'].sum() / 1024

        st.header(f"📊 Estate Analysis: {uploaded_file.name}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total VMs", total_vms)
        m2.metric("Total vCPUs", int(total_cpus))
        m3.metric("Total RAM (GB)", f"{total_ram_gb:,.0f}")

        # RHEL Savings
        rhel_vms = data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]
        num_rhel = len(rhel_vms)
        rhel_annual_savings = num_rhel * 800
        m4.metric("Annual RHEL Savings", f"${rhel_annual_savings:,}")

        # B. OpenShift Sizing Logic
        if "Standard" in node_type:
            n_cores, n_ram = 16, 64
        elif "Large" in node_type:
            n_cores, n_ram = 32, 128
        else:
            n_cores, n_ram = 64, 256

        eff_cores_req = total_cpus / cpu_ratio
        nodes_by_cpu = eff_cores_req / n_cores
        nodes_by_ram = total_ram_gb / n_ram
        worker_nodes = int(max(nodes_by_cpu, nodes_by_ram)) + 1 # N+1 for HA

        st.divider()
        st.header("🏗️ Proposed OpenShift Architecture")

        c1, c2, c3 = st.columns(3)
        c1.write(f"**Target Edition:** {edition}")
        c1.write(f"**Storage:** {storage_option}")

        c2.metric("Worker Nodes (N+1)", worker_nodes)
        c3.metric("Control Plane Nodes", 3)

        # C. People & Process Efficiency
        st.divider()
        st.header("👥 People & Process Transformation")

        tasks = {
            "Operational Task": ["Provisioning", "Patching", "Compliance Audit"],
            "Legacy Manual (Hrs)": [16, 40, 24],
            "OpenShift + ACM (Hrs)": [0.5, 4, 2]
        }
        pdf = pd.DataFrame(tasks)
        monthly_hours_saved = pdf["Legacy Manual (Hrs)"].sum() - pdf["OpenShift + ACM (Hrs)"].sum()

        col_t1, col_t2 = st.columns([2, 1])
        col_t1.table(pdf)
        col_t2.metric("Monthly Hours Reclaimed", f"{monthly_hours_saved} hrs")
        col_t2.write(f"Equivalent to **{round((monthly_hours_saved * 12)/1920, 1)} FTEs** per year.")

        # D. 5-Year TCO Summary
        st.divider()
        st.header("📈 5-Year TCO Projection")

        # Financial Logic
        ocp_sub_price = 2500 if "Plus" not in edition else 3500
        annual_ocp_sub = (worker_nodes * ocp_sub_price)
        annual_op_savings = (monthly_hours_saved * 12 * fte_rate)

        # VMware Baseline
        vmw_tco = [annual_vmware_cost * i for i in range(1, 6)]

        # OpenShift TCO (Year 1 includes migration effort)
        migration_effort_cost = (total_vms * 8 * fte_rate) # 8 hours per VM average
        ocp_net_annual = annual_ocp_sub - rhel_annual_savings - annual_op_savings

        ocp_tco = []
        current_ocp_spend = migration_effort_cost
        for i in range(1, 6):
            current_ocp_spend += max(0, (annual_ocp_sub - rhel_annual_savings)) # Licensing cost minus RHEL
            ocp_tco.append(current_ocp_spend)

        # Plotly Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=vmw_tco, name="VMware (As-Is)", line=dict(color='#6A6E73', width=2, dash='dash')))
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=ocp_tco, name="OpenShift (To-Be)", line=dict(color='#EE0000', width=4)))

        fig.update_layout(xaxis_title="Year", yaxis_title="Cumulative Cost ($)", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # Final ROI metrics
        total_savings = vmw_tco[-1] - ocp_tco[-1]
        r1, r2, r3 = st.columns(3)
        r1.metric("5-Year Net Savings", f"${int(total_savings):,}")
        r2.metric("Estimated ROI", f"{int((total_savings / ocp_tco[-1])*100)}%")
        r3.metric("Payback Period", "Year 2" if ocp_tco[1] < vmw_tco[1] else "Year 3")

        with st.expander("🔍 View Processed Data"):
            st.dataframe(data)

else:
    st.info("👋 **Welcome Specialist!** Please upload an RVTools `vInfo` CSV to begin the migration ROI analysis.")
    st.image("https://www.redhat.com/cms/managed-files/styles/xlarge/s3/2022-04/Management-Architecture-Diagram.png?itok=6lO_VjI_", caption="ACM Multi-Cluster Management Architecture")
