import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator | Full ROI Engine", page_icon="🚀", layout="wide")

# Currency Mapping
CURRENCIES = {
    "USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "ZAR (R)": "R", "AUD ($)": "A$", "SGD ($)": "S$"
}

# Custom Metric Styling
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

def generate_pdf_report(cust_name, metrics, financials, nodes, edition, currency_symbol, mig_details, node_specs, horizon, acm_status):
    pdf = ROIPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary for {cust_name}", ln=True)
    pdf.ln(5)

    # Inventory & Architecture
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Capacity & Forecasting", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Projection Horizon: {horizon} Years | Annual Workload Growth: {metrics['growth']}%", ln=True)
    pdf.cell(0, 10, f"- Initial VMs: {metrics['vms']} | Edition: {edition} (ACM: {acm_status})", ln=True)
    pdf.cell(0, 10, f"- Worker Nodes: {nodes} x ({node_specs['cores']} Cores / {node_specs['ram']}GB RAM)", ln=True)

    # Financials
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"2. Financials ({currency_symbol})", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- {horizon}-Year Net Savings: {currency_symbol}{financials['savings']:,.0f}", ln=True)
    pdf.cell(0, 10, f"- Total Migration Labor Cost: {currency_symbol}{financials['mig_cost']:,.0f}", ln=True)

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

    st.header("🌍 1. Localization & Data")
    curr_choice = st.selectbox("Select Currency", list(CURRENCIES.keys()))
    sym = CURRENCIES[curr_choice]
    uploaded_file = st.file_uploader("Upload RVTools CSV", type=["csv"])

    st.divider()
    st.header("📈 2. Growth & Forecasting")
    horizon = st.slider("Projection Horizon (Years)", 1, 7, 5)
    workload_growth = st.slider("Annual Workload Growth (%)", 0, 20, 5)
    sub_inflation = st.slider("Annual Subscription Inflation (%)", 0, 15, 10)

    st.divider()
    st.header("⚙️ 3. Sizing & Infrastructure")
    node_profile = st.selectbox("Node Profile", ["Standard (16c/64g)", "Large (32c/128g)", "Extra Large (64c/256g)", "Custom Spec"])
    if node_profile == "Custom Spec":
        n_cores = st.number_input("Cores", value=32)
        n_ram = st.number_input("RAM (GB)", value=128)
    else:
        n_cores, n_ram = (16, 64) if "Standard" in node_profile else (32, 128) if "Large" in node_profile else (64, 256)

    node_overhead = st.slider("System Overhead %", 0, 30, 10)
    cpu_ratio = st.slider("vCPU:Core Ratio", 1.0, 6.0, 3.0)

    st.divider()
    st.header("💰 4. VMware & Storage Costing")
    vmw_model = st.selectbox("VMware Model", ["VCF (Subscription)", "VVF (Subscription)", "Legacy ELA"])
    vmw_core_price = st.number_input(f"Annual {vmw_model} Price / Core ({sym})", value=350)
    stg_price_tb = st.number_input(f"Annual Storage Price / TB ({sym})", value=150)

    st.divider()
    st.header("🛠️ 5. Migration Complexity")
    with st.expander("T-Shirt Sizing Labor"):
        pct_easy = st.slider("% Easy", 0, 100, 70)
        pct_med = st.slider("% Medium", 0, 100 - pct_easy, 20)
        pct_hard = 100 - (pct_easy + pct_med)
        hrs_easy, hrs_med, hrs_hard = 4, 16, 60
        fte_rate = st.number_input(f"Consulting Rate ({sym})", value=120)

    st.divider()
    st.header("📦 6. OpenShift Pricing")
    with st.expander("Price List Details"):
        price_ove = st.number_input(f"OVE (Essentials) ({sym})", value=1500)
        price_oke = st.number_input(f"OKE (Engine) ({sym})", value=2200)
        price_ocp = st.number_input(f"OCP (Platform) ({sym})", value=3200)
        price_opp = st.number_input(f"OPP (Plus) ({sym})", value=4800)
        price_acm_virt = st.number_input(f"ACM for Virt ({sym})", value=600)
        price_acm_k8s = st.number_input(f"ACM for K8s ({sym})", value=900)

    target_edition = st.selectbox("Proposed Edition", ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"])

    # ACM Toggles
    include_acm = False
    if "OVE" in target_edition:
        include_acm = st.checkbox("Add ACM for Virtualization?")
    elif "OKE" in target_edition or "OCP" in target_edition:
        include_acm = st.checkbox("Add ACM for Kubernetes?")
    elif "OPP" in target_edition:
        include_acm = True
        st.info("ACM included in Plus.")

    rhel_value = st.number_input(f"RHEL Guest Value ({sym})", value=800)

# --- MAIN DASHBOARD LOGIC ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]
        vms_base, cpus_base, ram_sum_base, storage_base = len(data), data['CPUs'].sum(), data['Memory'].sum(), data['Disk_TB'].sum()

        # Efficiencies
        eff_cores_node = n_cores * (1 - node_overhead/100)
        eff_ram_node = n_ram * (1 - node_overhead/100)
        rhel_savings_base = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * rhel_value

        # Pricing Map
        pricing_map = {
            "OVE (Essentials)": {"base": price_ove, "acm": price_acm_virt},
            "OKE (Engine)": {"base": price_oke, "acm": price_acm_k8s},
            "OCP (Platform)": {"base": price_ocp, "acm": price_acm_k8s},
            "OPP (Plus)": {"base": price_opp, "acm": 0}
        }

        # CALCULATE MIGRATION LABOR (ONE-TIME)
        easy_count = int(vms_base * (pct_easy / 100))
        med_count = int(vms_base * (pct_med / 100))
        hard_count = vms_base - (easy_count + med_count)
        total_mig_hrs = (easy_count * hrs_easy) + (med_count * hrs_med) + (hard_count * hrs_hard)
        total_mig_cost = total_mig_hrs * fte_rate

        # 7-YEAR COMPOUND FORECASTING
        vmw_yearly_costs, ocp_yearly_costs, breakdown_data = [], [], []
        cum_ocp, cum_vmw = total_mig_cost, 0

        for yr in range(1, horizon + 1):
            growth_f = (1 + workload_growth/100)**(yr-1)
            inf_f = (1 + sub_inflation/100)**(yr-1)

            # Growth metrics
            vms_yr, cpus_yr = vms_base * growth_f, cpus_base * growth_f
            ram_yr, stg_yr = (ram_sum_base / 1024) * growth_f, storage_base * growth_f

            # Recalculate Nodes
            nodes_yr = int(max((cpus_yr/cpu_ratio)/eff_cores_node, ram_yr/eff_ram_node)) + 1

            # Yearly Financials
            vmw_yr_lic = max(cpus_yr/cpu_ratio, vms_yr * 2) * vmw_core_price
            vmw_yr_total = vmw_yr_lic + (stg_yr * stg_price_tb * 1.2)

            sub_price_yr = (pricing_map[target_edition]["base"] + (pricing_map[target_edition]["acm"] if include_acm else 0)) * inf_f
            auto_gain_yr = (fte_rate * 12 * 80) * (0.9 if include_acm else 0.4)
            ocp_yr_total = (nodes_yr * sub_price_yr) + (stg_yr * stg_price_tb) - (rhel_savings_base * growth_f) - auto_gain_yr

            cum_vmw += vmw_yr_total
            cum_ocp += ocp_yr_total
            vmw_yearly_costs.append(cum_vmw)
            ocp_yearly_costs.append(cum_ocp)

            breakdown_data.append({
                "Year": f"Year {yr}", "VMs": int(vms_yr), "Nodes": nodes_yr,
                "VMware Cost": f"{sym}{vmw_yr_total:,.0f}", "OpenShift Cost": f"{sym}{ocp_yr_total:,.0f}",
                "Annual Savings": f"{sym}{(vmw_yr_total - ocp_yr_total):,.0f}"
            })

        # --- RENDER ---
        st.header(f"💼 Business Case Analysis: {cust_name}")
        st.subheader("Summary Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Storage", f"{storage_base:.1f} TB")
        m2.metric("Year 1 Nodes", breakdown_data[0]['Nodes'])
        m3.metric("Migration Labor", f"{sym}{total_mig_cost:,.0f}")
        m4.metric(f"{horizon}-Year Net Savings", f"{sym}{(cum_vmw - cum_ocp):,.0f}")

        st.divider()
        st.subheader("Yearly Breakdown Table")
        st.table(pd.DataFrame(breakdown_data))

        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, horizon + 1)), y=vmw_yearly_costs, name="VMware Baseline", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=list(range(1, horizon + 1)), y=ocp_yearly_costs, name=f"Target: {target_edition}", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title=f"Cumulative {horizon}-Year TCO Projection", yaxis_title=f"Total Spend {sym}")
        st.plotly_chart(fig, use_container_width=True)

        # PDF Export
        metrics_p = {'vms': vms_base, 'cpus': int(cpus_base), 'storage_tb': storage_base, 'ratio': cpu_ratio, 'growth': workload_growth}
        finance_p = {'savings': cum_vmw - cum_ocp, 'mig_cost': total_mig_cost}
        node_specs = {'cores': n_cores, 'ram': n_ram}
        pdf_bytes = generate_pdf_report(cust_name, metrics_p, finance_p, breakdown_data[0]['Nodes'], target_edition, sym, {}, node_specs, horizon, "Yes" if include_acm else "No")
        st.download_button(f"📄 Download {horizon}-Year Proposal", data=pdf_bytes, file_name=f"V2O_{cust_name}.pdf")
