import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator | Migration ROI", page_icon="🚀", layout="wide")

# Currency Mapping
CURRENCIES = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "ZAR (R)": "R",
    "AUD ($)": "A$",
    "SGD ($)": "S$"
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

def generate_pdf_report(cust_name, metrics, financials, nodes, edition, currency_symbol, mig_details, acm_status):
    pdf = ROIPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary for {cust_name}", ln=True)
    pdf.ln(5)

    # Inventory Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Inventory & Architecture", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Total VMs: {metrics['vms']} | Target Nodes: {nodes} ({edition})", ln=True)
    pdf.cell(0, 10, f"- ACM Included: {acm_status}", ln=True)
    pdf.cell(0, 10, f"- Total Compute/Storage: {metrics['cpus']} vCPUs / {metrics['storage_tb']:.2f} TB", ln=True)

    # Migration Complexity
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Migration Complexity Breakdown", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Simple/Standard/Complex Mix: {mig_details['easy_count']}/{mig_details['med_count']}/{mig_details['hard_count']} VMs", ln=True)
    pdf.cell(0, 10, f"- Total Migration Effort: {mig_details['total_hrs']:,} Hours", ln=True)

    # Financials
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Financial Forecast", ln=True)
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
    st.header("⚙️ 2. Sizing & VMware Cost")
    cpu_ratio = st.slider("vCPU:Core Ratio", 1.0, 6.0, 3.0)
    node_size = st.selectbox("Node Instance", ["Standard (16c/64g)", "Large (32c/128g)", "Extra Large (64c/256g)"])
    vmw_model = st.selectbox("VMware Model", ["VCF (Subscription)", "VVF (Subscription)", "Legacy ELA"])
    vmw_core_price = st.number_input(f"Annual {vmw_model} Price / Core ({sym})", value=350)
    stg_price_tb = st.number_input(f"Annual Storage Price / TB ({sym})", value=150)

    st.divider()
    st.header("🛠️ 3. Migration Complexity")
    with st.expander("T-Shirt Sizing & Labor"):
        pct_easy = st.slider("% Easy (Lift & Shift)", 0, 100, 70)
        pct_med = st.slider("% Medium (Reconfig)", 0, 100 - pct_easy, 20)
        pct_hard = 100 - (pct_easy + pct_med)
        st.info(f"Hard/Complex Mix: {pct_hard}%")
        hrs_easy = st.number_input("Hrs per Easy VM", value=4)
        hrs_med = st.number_input("Hrs per Medium VM", value=16)
        hrs_hard = st.number_input("Hrs per Hard VM", value=60)
        fte_rate = st.number_input(f"Consulting Hourly Rate ({sym})", value=120)

    st.divider()
    st.header("💰 4. OpenShift Pricing")
    with st.expander("Subscription List Prices"):
        price_ove = st.number_input(f"OVE (Essentials) ({sym})", value=1500)
        price_oke = st.number_input(f"OKE (Engine) ({sym})", value=2200)
        price_ocp = st.number_input(f"OCP (Platform) ({sym})", value=3200)
        price_opp = st.number_input(f"OPP (Plus) ({sym})", value=4800)
        price_acm_virt = st.number_input(f"ACM for Virt ({sym})", value=600)
        price_acm_k8s = st.number_input(f"ACM for K8s ({sym})", value=900)

    target_edition = st.selectbox("Proposed Edition", ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"])

    # ACM Toggles (Context Aware)
    include_acm = False
    if "OVE" in target_edition:
        include_acm = st.checkbox("Add ACM for Virtualization?")
    elif "OKE" in target_edition or "OCP" in target_edition:
        include_acm = st.checkbox("Add ACM for Kubernetes?")
    elif "OPP" in target_edition:
        st.info("ACM Included in OPP.")
        include_acm = True

    rhel_value = st.number_input(f"RHEL Guest Value ({sym})", value=800)

# --- MAIN DASHBOARD LOGIC ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]
        vms, cpus, ram_sum, storage = len(data), data['CPUs'].sum(), data['Memory'].sum(), data['Disk_TB'].sum()

        # Labor Math
        easy_count = int(vms * (pct_easy / 100))
        med_count = int(vms * (pct_med / 100))
        hard_count = vms - (easy_count + med_count)
        total_mig_hrs = (easy_count * hrs_easy) + (med_count * hrs_med) + (hard_count * hrs_hard)
        total_mig_cost = total_mig_hrs * fte_rate

        st.header(f"💼 Business Case Analysis: {cust_name}")

        # Summary Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total VMs", vms)
        m2.metric("Total Storage", f"{storage:.1f} TB")
        m3.metric("Migration Effort", f"{total_mig_hrs:,} Hrs")
        m4.metric("Migration Labor", f"{sym}{total_mig_cost:,.0f}")

        # VMware Financials
        est_cores = max(cpus / cpu_ratio, vms * 2)
        vmw_annual = (est_cores * vmw_core_price) + (storage * stg_price_tb * 1.2)

        # OpenShift Sizing
        n_cores, n_ram = (16, 64) if "Standard" in node_size else (32, 128) if "Large" in node_size else (64, 256)
        req_nodes = int(max((cpus/cpu_ratio)/n_cores, (ram_sum/1024)/n_ram)) + 1

        # Selected Pricing
        pricing_map = {
            "OVE (Essentials)": {"base": price_ove, "acm": price_acm_virt},
            "OKE (Engine)": {"base": price_oke, "acm": price_acm_k8s},
            "OCP (Platform)": {"base": price_ocp, "acm": price_acm_k8s},
            "OPP (Plus)": {"base": price_opp, "acm": 0}
        }

        ocp_base = pricing_map[target_edition]["base"]
        ocp_acm = pricing_map[target_edition]["acm"] if include_acm else 0
        ocp_annual_sub = req_nodes * (ocp_base + ocp_acm)
        rhel_savings = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * rhel_value

        # TCO Logic
        vmw_5yr = [vmw_annual * i for i in range(1, 6)]
        ocp_5yr = []
        current_ocp = total_mig_cost # Upfront labor
        for i in range(1, 6):
            # Subscription + Storage - RHEL Savings - Operational Automation Gain
            automation_gain = (fte_rate * 12 * 80) * (0.9 if include_acm else 0.4)
            current_ocp += (ocp_annual_sub + (storage * stg_price_tb) - rhel_savings - automation_gain)
            ocp_5yr.append(current_ocp)

        # Charts
        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=vmw_5yr, name="VMware VCF", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=ocp_5yr, name=f"Target: {target_edition}", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title=f"Cumulative 5-Year TCO ({sym})", yaxis_title=f"Total Spend {sym}")
        st.plotly_chart(fig, use_container_width=True)

        # PDF Export
        st.divider()
        metrics = {'vms': vms, 'cpus': int(cpus), 'storage_tb': storage, 'ratio': cpu_ratio}
        financials = {'savings': vmw_5yr[-1] - ocp_5yr[-1], 'mig_cost': total_mig_cost}
        mig_details = {'easy_count': easy_count, 'med_count': med_count, 'hard_count': hard_count, 'total_hrs': total_mig_hrs}
        acm_status = "Yes" if include_acm else "No"

        pdf_bytes = generate_pdf_report(cust_name, metrics, financials, req_nodes, target_edition, sym, mig_details, acm_status)
        st.download_button(f"📄 Download Professional Proposal ({sym})", data=pdf_bytes, file_name=f"V2O_Proposal_{cust_name}.pdf")
