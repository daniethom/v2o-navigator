import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator | Migration ROI", page_icon="🚀", layout="wide")

# Currency Mapping
CURRENCIES = {"USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "ZAR (R)": "R", "AUD ($)": "A$", "SGD ($)": "S$"}

# Custom Metric Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #EE0000; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATION (Updated for 7 years) ---
class ROIPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'V2O Navigator: Infrastructure Migration Analysis', 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(cust_name, metrics, financials, nodes, edition, currency_symbol, mig_details, node_specs, horizon):
    pdf = ROIPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary for {cust_name}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Capacity & Forecasting", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Projection Horizon: {horizon} Years", ln=True)
    pdf.cell(0, 10, f"- Initial VMs: {metrics['vms']} | Initial Nodes: {nodes}", ln=True)
    pdf.cell(0, 10, f"- Annual Workload Growth: {metrics['growth']}%", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"2. Financials ({currency_symbol})", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- {horizon}-Year Net Savings: {currency_symbol}{financials['savings']:,.0f}", ln=True)
    pdf.cell(0, 10, f"- Total Migration Labor: {currency_symbol}{financials['mig_cost']:,.0f}", ln=True)

    return bytes(pdf.output())

# --- DATA PROCESSING ---
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
    st.header("📈 2. Growth & Forecasting")
    horizon = st.slider("Projection Horizon (Years)", 1, 7, 5)
    workload_growth = st.slider("Annual Workload Growth (%)", 0, 20, 5, help="Industry standard is typically 5-10% for VMs.")
    sub_inflation = st.slider("Annual Subscription Inflation (%)", 0, 15, 10, help="Expected yearly price increase.")

    st.divider()
    st.header("⚙️ 3. Sizing & Infrastructure")
    node_profile = st.selectbox("Node Profile", ["Standard (16c/64g)", "Large (32c/128g)", "Custom Spec"])
    if node_profile == "Custom Spec":
        n_cores, n_ram = st.number_input("Cores", value=32), st.number_input("RAM (GB)", value=128)
    else:
        n_cores, n_ram = (16, 64) if "Standard" in node_profile else (32, 128)

    node_overhead = st.slider("System Overhead %", 0, 30, 10)
    cpu_ratio = st.slider("vCPU:Core Ratio", 1.0, 6.0, 3.0)

    st.divider()
    st.header("💰 4. Pricing & Labor")
    vmw_core_price = st.number_input(f"Annual VMware Core Price ({sym})", value=350)
    stg_price_tb = st.number_input(f"Annual Storage Price / TB ({sym})", value=150)
    target_edition = st.selectbox("Proposed Edition", ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"])
    fte_rate = st.number_input(f"Consulting Rate ({sym})", value=120)

# --- MAIN DASHBOARD ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]

        # Base Data
        vms_base, cpus_base = len(data), data['CPUs'].sum()
        ram_sum_base, storage_base = data['Memory'].sum(), data['Disk_TB'].sum()

        # Sizing Calculations Logic for Year 1
        eff_cores_node = n_cores * (1 - node_overhead/100)
        eff_ram_node = n_ram * (1 - node_overhead/100)
        rhel_savings_base = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * 800

        # COMPOUND CALCULATION ENGINE
        vmw_yearly_costs = []
        ocp_yearly_costs = []
        breakdown_data = []

        cum_ocp = (vms_base * 8 * fte_rate) # Migration Setup Cost (Year 0 proxy)
        cum_vmw = 0

        for yr in range(1, horizon + 1):
            # 1. Apply Workload Growth
            growth_factor = (1 + workload_growth/100)**(yr-1)
            vms_yr = vms_base * growth_factor
            cpus_yr = cpus_base * growth_factor
            ram_yr = (ram_sum_base / 1024) * growth_factor
            stg_yr = storage_base * growth_factor

            # 2. Recalculate Node Requirements for Growth
            nodes_yr = int(max((cpus_yr/cpu_ratio)/eff_cores_node, ram_yr/eff_ram_node)) + 1

            # 3. Apply Subscription Inflation
            inflation_factor = (1 + sub_inflation/100)**(yr-1)
            sub_price_yr = (4800 if "OPP" in target_edition else 3200) * inflation_factor

            # 4. Yearly Totals
            vmw_yr_total = (max(cpus_yr/cpu_ratio, vms_yr * 2) * vmw_core_price) + (stg_yr * stg_price_tb * 1.2)
            ocp_yr_total = (nodes_yr * sub_price_yr) + (stg_yr * stg_price_tb) - (rhel_savings_base * growth_factor)

            cum_vmw += vmw_yr_total
            cum_ocp += ocp_yr_total

            vmw_yearly_costs.append(cum_vmw)
            ocp_yearly_costs.append(cum_ocp)

            breakdown_data.append({
                "Year": f"Year {yr}",
                "VMs": int(vms_yr),
                "Nodes Required": nodes_yr,
                "VMware Cost": f"{sym}{vmw_yr_total:,.0f}",
                "OpenShift Cost": f"{sym}{ocp_yr_total:,.0f}",
                "Annual Savings": f"{sym}{(vmw_yr_total - ocp_yr_total):,.0f}"
            })

        st.header(f"💼 Business Case Analysis: {cust_name}")

        # Summary Visuals
        st.subheader("Yearly Breakdown Table (#10)")
        st.table(pd.DataFrame(breakdown_data))

        # TCO Chart (Updated for N Years)
        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, horizon + 1)), y=vmw_yearly_costs, name="VMware Baseline", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=list(range(1, horizon + 1)), y=ocp_yearly_costs, name="OpenShift Target", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title=f"Cumulative {horizon}-Year TCO Projection", xaxis_title="Year", yaxis_title=f"Total Spend {sym}")
        st.plotly_chart(fig, use_container_width=True)

        # PDF Export
        st.divider()
        metrics = {'vms': vms_base, 'cpus': int(cpus_base), 'storage_tb': storage_base, 'ratio': cpu_ratio, 'growth': workload_growth}
        financials = {'savings': vmw_yearly_costs[-1] - ocp_yearly_costs[-1], 'mig_cost': (vms_base * 8 * fte_rate)}
        pdf_bytes = generate_pdf_report(cust_name, metrics, financials, breakdown_data[0]['Nodes Required'], target_edition, sym, {}, {}, horizon)
        st.download_button(f"📄 Download {horizon}-Year Executive Proposal", data=pdf_bytes, file_name=f"V2O_{cust_name}.pdf")
