import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator | Migration ROI", page_icon="🚀", layout="wide")

# Currency Mapping
CURRENCIES = {
    "USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "ZAR (R)": "R", "AUD ($)": "A$", "SGD ($)": "S$"
}

# Custom Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #EE0000; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATION ENGINE ---
class ROIPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'V2O Navigator: Infrastructure Migration Analysis', 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(cust_name, metrics, financials, nodes, edition, currency_symbol, mig_details, acm_status, node_specs):
    pdf = ROIPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary for {cust_name}", ln=True)
    pdf.ln(5)

    # Inventory & Architecture
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Inventory & Architecture", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Total VMs: {metrics['vms']} | Edition: {edition} (ACM: {acm_status})", ln=True)
    pdf.cell(0, 10, f"- Worker Nodes: {nodes} x ({node_specs['cores']} Cores / {node_specs['ram']}GB RAM)", ln=True)
    pdf.cell(0, 10, f"- Resource Overhead Buffer: {node_specs['overhead']}%", ln=True)

    # Migration & Financials
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Project Financials", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- 5-Year Net Savings: {currency_symbol}{financials['savings']:,.0f}", ln=True)
    pdf.cell(0, 10, f"- Est. Migration Labor Cost: {currency_symbol}{financials['mig_cost']:,.0f}", ln=True)

    return bytes(pdf.output())

# --- RESILIENT DATA PROCESSING ---
def process_rvtools(file):
    try:
        df = pd.read_csv(file)
        df.columns = [str(c).strip() for c in df.columns]
        mapping = {
            'VM': next((c for c in df.columns if c.lower() in ['vm', 'virtual machine']), None),
            'CPUs': next((c for c in df.columns if c.lower() in ['cpus', 'vcpu']), None),
            'Memory': next((c for c in df.columns if 'memory' in c.lower()), None),
            'OS': next((c for c in df.columns if 'os according to' in c.lower() or c.lower() == 'os'), None),
            'Disk': next((c for c in df.columns if ('capacity' in c.lower() or 'mib' in c.lower()) and 'disk' in c.lower()), None)
        }
        if None in mapping.values(): return None
        df_clean = df[[mapping['VM'], mapping['CPUs'], mapping['Memory'], mapping['OS'], mapping['Disk']]].copy()
        df_clean.columns = ['VM', 'CPUs', 'Memory', 'OS', 'Disk_MiB']
        for col in ['CPUs', 'Memory', 'Disk_MiB']:
            df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df_clean['Disk_TB'] = df_clean['Disk_MiB'] / 1048576
        return df_clean
    except: return None

# --- SIDEBAR: ALL CONTROLS ---
with st.sidebar:
    st.image("https://www.redhat.com/cms/managed-files/Logo-RedHat-OpenShift-A-Standard-RGB.png", width=200)

    st.header("🌍 1. Localization")
    curr_choice = st.selectbox("Select Currency", list(CURRENCIES.keys()))
    sym = CURRENCIES[curr_choice]
    uploaded_file = st.file_uploader("Upload RVTools CSV", type=["csv"])

    st.divider()
    st.header("⚙️ 2. Node Sizing & Overhead (#3)")
    node_profile = st.selectbox("Worker Node Profile",
                                ["Standard (16c/64g)", "Large (32c/128g)", "Extra Large (64c/256g)", "Custom Spec"])

    if node_profile == "Custom Spec":
        n_cores = st.number_input("Node Physical Cores", value=32)
        n_ram = st.number_input("Node RAM (GB)", value=128)
    else:
        n_cores, n_ram = (16, 64) if "Standard" in node_profile else (32, 128) if "Large" in node_profile else (64, 256)

    node_overhead = st.slider("System Overhead % (OS/Kube)", 0, 30, 10, help="Capacity reserved for the platform itself.")
    cpu_ratio = st.slider("vCPU:Core Consolidation Ratio", 1.0, 6.0, 3.0)

    st.divider()
    st.header("💰 3. Infrastructure Pricing")
    vmw_core_price = st.number_input(f"Annual VMware Core Price ({sym})", value=350)
    stg_price_tb = st.number_input(f"Annual Storage Price / TB ({sym})", value=150)

    st.divider()
    st.header("🛠️ 4. Migration Complexity")
    with st.expander("Labor Breakdown"):
        pct_easy = st.slider("% Easy", 0, 100, 70)
        pct_med = st.slider("% Medium", 0, 100 - pct_easy, 20)
        pct_hard = 100 - (pct_easy + pct_med)
        hrs_easy, hrs_med, hrs_hard = 4, 16, 60
        fte_rate = st.number_input(f"Consulting Rate ({sym})", value=120)

    st.divider()
    st.header("📦 5. Platform Editions")
    with st.expander("Price List"):
        price_ove, price_oke, price_ocp, price_opp = 1500, 2200, 3200, 4800
        price_acm_virt, price_acm_k8s = 600, 900

    target_edition = st.selectbox("Proposed Edition", ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"])
    include_acm = st.checkbox("Include ACM?") if "OPP" not in target_edition else True
    rhel_value = st.number_input(f"RHEL Guest Value ({sym})", value=800)

# --- MAIN DASHBOARD ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]
        vms, cpus, ram_sum, storage = len(data), data['CPUs'].sum(), data['Memory'].sum(), data['Disk_TB'].sum()

        # SIZING LOGIC (#3)
        # We apply the overhead to the node's capacity
        eff_cores_per_node = n_cores * (1 - node_overhead/100)
        eff_ram_per_node = n_ram * (1 - node_overhead/100)

        # Calculate nodes based on CPU vs RAM bottleneck
        nodes_by_cpu = (cpus / cpu_ratio) / eff_cores_per_node
        nodes_by_ram = (ram_sum / 1024) / eff_ram_per_node
        req_nodes = int(max(nodes_by_cpu, nodes_by_ram)) + 1 # N+1 for HA

        # Financials
        easy_count, med_count = int(vms * (pct_easy/100)), int(vms * (pct_med/100))
        hard_count = vms - (easy_count + med_count)
        total_mig_cost = ((easy_count * hrs_easy) + (med_count * hrs_med) + (hard_count * hrs_hard)) * fte_rate

        st.header(f"💼 Business Case Analysis: {cust_name}")

        # Summary Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Target Worker Nodes", f"{req_nodes} (N+1)")
        m2.metric("Effective Cores/Node", f"{eff_cores_per_node:.1f}")
        m3.metric("Effective RAM/Node", f"{eff_ram_per_node:.1f} GB")
        m4.metric("Migration Labor", f"{sym}{total_mig_cost:,.0f}")

        # TCO Charts
        vmw_annual = (max(cpus / cpu_ratio, vms * 2) * vmw_core_price) + (storage * stg_price_tb * 1.2)
        ocp_sub = req_nodes * (4800 if "OPP" in target_edition else 3200) # Simplified sub for demo

        vmw_5yr = [vmw_annual * i for i in range(1, 6)]
        ocp_5yr = []
        curr_ocp = total_mig_cost
        for i in range(1, 6):
            # Applying automation savings based on ACM
            auto_gain = (fte_rate * 12 * 80) * (0.9 if include_acm else 0.4)
            rhel_savings = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * rhel_value
            curr_ocp += (ocp_sub + (storage * stg_price_tb) - rhel_savings - auto_gain)
            ocp_5yr.append(curr_ocp)

        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=vmw_5yr, name="VMware Baseline", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=ocp_5yr, name="OpenShift Target", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title=f"Cumulative 5-Year TCO ({sym})", yaxis_title=f"Total Spend {sym}")
        st.plotly_chart(fig, use_container_width=True)

        # PDF Export Update
        st.divider()
        metrics = {'vms': vms, 'cpus': int(cpus), 'storage_tb': storage, 'ratio': cpu_ratio}
        financials = {'savings': vmw_5yr[-1] - ocp_5yr[-1], 'mig_cost': total_mig_cost}
        mig_details = {'easy_count': easy_count, 'med_count': med_count, 'hard_count': hard_count}
        node_specs = {'cores': n_cores, 'ram': n_ram, 'overhead': node_overhead}

        pdf_bytes = generate_pdf_report(cust_name, metrics, financials, req_nodes, target_edition, sym, mig_details, "Yes" if include_acm else "No", node_specs)
        st.download_button(f"📄 Download Professional Proposal ({sym})", data=pdf_bytes, file_name=f"V2O_Proposal_{cust_name}.pdf")
