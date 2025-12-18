import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator | ROI Engine", page_icon="🚀", layout="wide")

# Currency Mapping
CURRENCIES = {"USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "ZAR (R)": "R", "AUD ($)": "A$", "SGD ($)": "S$"}

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
        self.cell(0, 10, 'V2O Navigator Analysis', 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(cust_name, financials, sym, horizon):
    pdf = ROIPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary: {cust_name}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Projection Horizon: {horizon} Years", ln=True)
    pdf.cell(0, 10, f"Total Net Savings: {sym}{financials['savings']:,.0f}", ln=True)
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
    st.header("⚙️ 3. Node Sizing & Overhead")
    node_profile = st.selectbox("Worker Node Profile",
                                ["Standard (16c/64g)", "Large (32c/128g)", "Extra Large (64c/256g)", "Custom Spec"])

    if node_profile == "Custom Spec":
        n_cores = st.number_input("Node Physical Cores", value=32)
        n_ram = st.number_input("Node RAM (GB)", value=128)
    else:
        n_cores, n_ram = (16, 64) if "Standard" in node_profile else (32, 128) if "Large" in node_profile else (64, 256)

    node_overhead = st.slider("System Overhead %", 0, 30, 10)
    cpu_ratio = st.slider("vCPU:Core Consolidation Ratio", 1.0, 6.0, 3.0)

    st.divider()
    st.header("💰 4. VMware & Storage Costing")
    vmw_model = st.selectbox("VMware Model", ["VCF (Subscription)", "VVF (Subscription)", "Legacy ELA"])
    vmw_core_price = st.number_input(f"Annual VMware Core Price ({sym})", value=350)
    stg_price_tb = st.number_input(f"Annual Storage Price / TB ({sym})", value=150)

    st.divider()
    st.header("🛠️ 5. Migration Complexity")
    with st.expander("T-Shirt Sizing Labor"):
        pct_easy = st.slider("% Easy (Lift & Shift)", 0, 100, 70)
        pct_med = st.slider("% Medium (Reconfig)", 0, 100 - pct_easy, 20)
        pct_hard = 100 - (pct_easy + pct_med)
        st.info(f"Hard/Complex Mix: {pct_hard}%")
        hrs_easy = st.number_input("Hrs per Easy VM", value=4)
        hrs_med = st.number_input("Hrs per Medium VM", value=16)
        hrs_hard = st.number_input("Hrs per Hard VM", value=60)
        fte_rate = st.number_input(f"Consulting Hourly Rate ({sym})", value=120)

    st.divider()
    st.header("📦 6. OpenShift Pricing")
    with st.expander("Subscription List Prices"):
        price_ove = st.number_input(f"OVE ({sym})", value=1500)
        price_oke = st.number_input(f"OKE ({sym})", value=2200)
        price_ocp = st.number_input(f"OCP ({sym})", value=3200)
        price_opp = st.number_input(f"OPP ({sym})", value=4800)
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
        st.info("ACM Included in OPP.")

    rhel_value = st.number_input(f"RHEL Guest Value ({sym})", value=800)

# --- MAIN DASHBOARD LOGIC ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]
        vms_base, cpus_base, ram_sum_base, storage_base = len(data), data['CPUs'].sum(), data['Memory'].sum(), data['Disk_TB'].sum()

        # Sizing Logic
        eff_cores = n_cores * (1 - node_overhead/100)
        eff_ram = n_ram * (1 - node_overhead/100)
        rhel_savings_base = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * rhel_value

        # Pricing Map
        pricing_map = {
            "OVE (Essentials)": {"base": price_ove, "acm": price_acm_virt},
            "OKE (Engine)": {"base": price_oke, "acm": price_acm_k8s},
            "OCP (Platform)": {"base": price_ocp, "acm": price_acm_k8s},
            "OPP (Plus)": {"base": price_opp, "acm": 0}
        }

        # One-time Migration Cost (Complexity Based)
        easy_c, med_c = int(vms_base * (pct_easy/100)), int(vms_base * (pct_med/100))
        hard_c = vms_base - (easy_c + med_c)
        total_mig_cost = ((easy_c * hrs_easy) + (med_c * hrs_med) + (hard_c * hrs_hard)) * fte_rate

        # 7-YEAR COMPOUND FORECASTING
        vmw_cum_list, ocp_cum_list, breakdown_data = [], [], []
        cum_vmw, cum_ocp = 0, total_mig_cost

        for yr in range(1, horizon + 1):
            growth_f = (1 + workload_growth/100)**(yr-1)
            inf_f = (1 + sub_inflation/100)**(yr-1)

            vms_yr, cpus_yr = vms_base * growth_f, cpus_base * growth_f
            ram_yr, stg_yr = (ram_sum_base / 1024) * growth_f, storage_base * growth_f

            nodes_yr = int(max((cpus_yr/cpu_ratio)/eff_cores, ram_yr/eff_ram)) + 1

            vmw_yr_total = (max(cpus_yr/cpu_ratio, vms_yr * 2) * vmw_core_price) + (stg_yr * stg_price_tb * 1.2)

            sub_price_yr = (pricing_map[target_edition]["base"] + (pricing_map[target_edition]["acm"] if include_acm else 0)) * inf_f
            auto_gain_yr = (fte_rate * 12 * 80) * (0.9 if include_acm else 0.4)
            ocp_yr_total = (nodes_yr * sub_price_yr) + (stg_yr * stg_price_tb) - (rhel_savings_base * growth_f) - auto_gain_yr

            cum_vmw += vmw_yr_total
            cum_ocp += ocp_yr_total
            vmw_cum_list.append(cum_vmw)
            ocp_cum_list.append(cum_ocp)

            breakdown_data.append({
                "Year": f"Year {yr}",
                "Annual VMware": f"{sym}{vmw_yr_total:,.0f}",
                "Annual OpenShift": f"{sym}{ocp_yr_total:,.0f}",
                "Cumulative Savings": f"{sym}{(cum_vmw - cum_ocp):,.0f}"
            })

        # --- RENDER ---
        st.header(f"💼 Business Case: {cust_name}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Upfront Migration Cost", f"{sym}{total_mig_cost:,.0f}")
        m2.metric(f"Year 1 Nodes", breakdown_data[0]['Annual OpenShift'].split(sym)[0]) # Logic Check
        m2.metric(f"Year 1 Nodes", int(max((cpus_base/cpu_ratio)/eff_cores, (ram_sum_base/1024)/eff_ram)) + 1)
        m3.metric(f"{horizon}-Year Total Savings", f"{sym}{(cum_vmw - cum_ocp):,.0f}")
        m4.metric("Avg Annual Workload Growth", f"{workload_growth}%")

        st.divider()
        st.subheader("Yearly Financial Breakdown")
        st.table(pd.DataFrame(breakdown_data))

        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, horizon + 1)), y=vmw_cum_list, name="Cumulative VMware Spend", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=list(range(1, horizon + 1)), y=ocp_cum_list, name="Cumulative OpenShift Spend", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title=f"Cumulative {horizon}-Year TCO Projection", xaxis_title="Year", yaxis_title=f"Total Spend ({sym})")
        st.plotly_chart(fig, use_container_width=True)

        pdf_bytes = generate_pdf_report(cust_name, {'savings': cum_vmw - cum_ocp}, sym, horizon)
        st.download_button(f"📄 Download {horizon}-Year Proposal", data=pdf_bytes, file_name=f"V2O_{cust_name}.pdf")
else:
    st.info("👋 Welcome. Please upload an RVTools `vInfo` CSV in the sidebar.")
