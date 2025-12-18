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
    "AUD ($)": "A$"
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

def generate_pdf_report(cust_name, metrics, financials, nodes, edition, currency_symbol, mig_details):
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
    pdf.cell(0, 10, f"- Total Compute/Storage: {metrics['cpus']} vCPUs / {metrics['storage_tb']:.2f} TB", ln=True)

    # Migration Complexity
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Migration Complexity Breakdown", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Simple (Easy): {mig_details['easy_count']} VMs", ln=True)
    pdf.cell(0, 10, f"- Standard (Medium): {mig_details['med_count']} VMs", ln=True)
    pdf.cell(0, 10, f"- Complex (Hard): {mig_details['hard_count']} VMs", ln=True)
    pdf.cell(0, 10, f"- Total Migration Effort: {mig_details['total_hrs']:,} Hours", ln=True)

    # Financials
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Financial Forecast", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- 5-Year Net Savings: {currency_symbol}{financials['savings']:,.0f}", ln=True)
    pdf.cell(0, 10, f"- Total Migration Labor Cost: {currency_symbol}{financials['mig_cost']:,.0f}", ln=True)

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

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.image("https://www.redhat.com/cms/managed-files/Logo-RedHat-OpenShift-A-Standard-RGB.png", width=200)

    # FEATURE #1: Multi-Currency
    st.header("🌍 Localization")
    curr_choice = st.selectbox("Select Currency", list(CURRENCIES.keys()))
    sym = CURRENCIES[curr_choice]

    uploaded_file = st.file_uploader("Upload RVTools CSV", type=["csv"])

    st.divider()
    st.header("⚙️ Sizing & Costing")
    cpu_ratio = st.slider("vCPU:Core Ratio", 1.0, 6.0, 3.0)
    vmw_core_price = st.number_input(f"Annual VMware Price / Core ({sym})", value=350)

    st.divider()
    st.header("🛠️ Migration Complexity (#8)")
    with st.expander("T-Shirt Sizing Details"):
        # Sliders for % mix
        pct_easy = st.slider("% Easy (Lift & Shift)", 0, 100, 70)
        pct_med = st.slider("% Medium (Reconfig)", 0, 100 - pct_easy, 20)
        pct_hard = 100 - (pct_easy + pct_med)
        st.info(f"Hard/Complex: {pct_hard}%")

        st.write("---")
        # Effort hours per category
        hrs_easy = st.number_input("Hrs per Easy VM", value=4)
        hrs_med = st.number_input("Hrs per Medium VM", value=16)
        hrs_hard = st.number_input("Hrs per Hard VM", value=60)

    st.divider()
    st.header("💰 Platform Pricing")
    with st.expander("OpenShift List Prices"):
        price_ove = st.number_input(f"OVE Price ({sym})", value=1500)
        price_opp = st.number_input(f"OPP Price ({sym})", value=4800)
    target_edition = st.selectbox("Proposed Edition", ["OVE (Essentials)", "OPP (Plus)"])
    fte_rate = st.number_input(f"Consulting Hourly Rate ({sym})", value=120)

# --- MAIN DASHBOARD ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]
        vms, cpus, storage = len(data), data['CPUs'].sum(), data['Disk_TB'].sum()

        # FEATURE #8 Logic: Labor Calculations
        easy_count = int(vms * (pct_easy / 100))
        med_count = int(vms * (pct_med / 100))
        hard_count = vms - (easy_count + med_count)

        total_mig_hrs = (easy_count * hrs_easy) + (med_count * hrs_med) + (hard_count * hrs_hard)
        total_mig_cost = total_mig_hrs * fte_rate

        st.header(f"💼 Business Case: {cust_name}")

        # Summary Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Total VMs", vms)
        m2.metric("Est. Migration Effort", f"{total_mig_hrs:,} Hrs")
        m3.metric("Migration Labor Cost", f"{sym}{total_mig_cost:,.0f}")

        # Financial Baseline
        est_cores = max(cpus / cpu_ratio, vms * 2)
        vmw_annual = est_cores * vmw_core_price

        # Sizing
        req_nodes = int(max((cpus/cpu_ratio)/16, (data['Memory'].sum()/1024)/64)) + 1
        ocp_sub = req_nodes * (price_opp if "Plus" in target_edition else price_ove)

        # TCO Logic
        vmw_5yr = [vmw_annual * i for i in range(1, 6)]
        ocp_5yr = []
        current_ocp = total_mig_cost # Year 0 / Start cost is the complexity-based labor
        for i in range(1, 6):
            current_ocp += (ocp_sub + (storage * 150)) # Adding generic storage price
            ocp_5yr.append(current_ocp)

        # Charts
        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=vmw_5yr, name="VMware VCF", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=ocp_5yr, name="OpenShift Target", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title=f"5-Year TCO ({sym})", yaxis_title=f"Total Spend {sym}")
        st.plotly_chart(fig, use_container_width=True)

        # PDF Export with new details
        st.divider()
        metrics = {'vms': vms, 'cpus': int(cpus), 'storage_tb': storage, 'ratio': cpu_ratio}
        financials = {'savings': vmw_5yr[-1] - ocp_5yr[-1], 'mig_cost': total_mig_cost}
        mig_details = {'easy_count': easy_count, 'med_count': med_count, 'hard_count': hard_count, 'total_hrs': total_mig_hrs}

        pdf_bytes = generate_pdf_report(cust_name, metrics, financials, req_nodes, target_edition, sym, mig_details)
        st.download_button(f"📄 Download Professional Services Estimate ({sym})", data=pdf_bytes, file_name=f"V2O_Proposal_{cust_name}.pdf")
