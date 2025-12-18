import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP & THEME ---
st.set_page_config(page_title="V2O Navigator | Full ROI Engine", page_icon="🚀", layout="wide")

CURRENCIES = {
    "USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "ZAR (R)": "R", "AUD ($)": "A$", "SGD ($)": "S$"
}

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #EE0000; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATOR ---
class ROIPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'V2O Navigator: Infrastructure Migration Analysis', 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(cust_name, financials, sym, horizon, metrics, edition):
    pdf = ROIPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary: {cust_name}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Analysis Horizon: {horizon} Years", ln=True)
    pdf.cell(0, 10, f"Target Edition: {edition}", ln=True)
    pdf.cell(0, 10, f"Net Cumulative Savings: {sym}{financials['savings']:,.0f}", ln=True)
    pdf.cell(0, 10, f"Upfront Migration Labor: {sym}{financials['mig_cost']:,.0f}", ln=True)
    return bytes(pdf.output())

# --- DATA PARSER ---
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

# --- SIDEBAR: ALL FEATURES ENABLED ---
with st.sidebar:
    st.image("https://www.redhat.com/cms/managed-files/Logo-RedHat-OpenShift-A-Standard-RGB.png", width=200)

    st.header("🌍 1. Localization & Data")
    curr_choice = st.selectbox("Currency", list(CURRENCIES.keys()))
    sym = CURRENCIES[curr_choice]
    uploaded_file = st.file_uploader("Upload RVTools vInfo CSV", type=["csv"])

    st.divider()
    st.header("📈 2. Forecasting & Growth")
    horizon = st.slider("Projection Horizon (Years)", 1, 7, 5)
    workload_growth = st.slider("Annual Workload Growth (%)", 0, 20, 5)
    sub_inflation = st.slider("Annual Price Inflation (%)", 0, 15, 10)

    st.divider()
    st.header("⚙️ 3. Physical Node Sizing")
    node_profile = st.selectbox("Node Hardware Profile", ["Standard (32c/128g)", "High Density (64c/256g)", "Custom Spec"])
    if node_profile == "Custom Spec":
        n_cores = st.number_input("Cores per Node", value=64)
        n_ram = st.number_input("RAM per Node (GB)", value=256)
    else:
        n_cores, n_ram = (32, 128) if "Standard" in node_profile else (64, 256)

    node_overhead = st.slider("System Overhead %", 0, 30, 10)
    cpu_ratio = st.slider("vCPU:Core Ratio", 1.0, 6.0, 3.0)

    st.divider()
    st.header("💰 4. VMware & Storage Cost")
    vmw_model = st.selectbox("VMware Model", ["VCF (Cloud Foundation)", "VVF (vSphere Foundation)"])
    vmw_core_price = st.number_input(f"VMware Price / Core ({sym})", value=350)
    stg_price_tb = st.number_input(f"Storage Price / TB ({sym})", value=150)

    st.divider()
    st.header("🛠️ 5. Migration Complexity")
    with st.expander("T-Shirt Sizing Labor"):
        pct_easy = st.slider("% Easy", 0, 100, 70)
        pct_med = st.slider("% Medium", 0, 100 - pct_easy, 20)
        pct_hard = 100 - (pct_easy + pct_med)
        hrs_easy = st.number_input("Hrs/Easy VM", value=4)
        hrs_med = st.number_input("Hrs/Medium VM", value=16)
        hrs_hard = st.number_input("Hrs/Hard VM", value=60)
        fte_rate = st.number_input(f"Consulting Rate ({sym})", value=120)

    st.divider()
    st.header("📦 6. OpenShift Pricing")
    with st.expander("Adjust List Prices"):
        p_ove = st.number_input("OVE Base Price", value=1500)
        p_oke = st.number_input("OKE Base Price", value=2200)
        p_ocp = st.number_input("OCP Base Price", value=3200)
        p_opp = st.number_input("OPP Base Price", value=4800)
        p_acm_v = st.number_input("ACM Virt Add-on", value=600)
        p_acm_k = st.number_input("ACM K8s Add-on", value=900)

    target_edition = st.selectbox("Edition", ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"])

    # ACM Logic
    include_acm = False
    if "OVE" in target_edition:
        include_acm = st.checkbox("Add ACM for Virt?")
    elif "OKE" in target_edition or "OCP" in target_edition:
        include_acm = st.checkbox("Add ACM for K8s?")
    elif "OPP" in target_edition:
        include_acm = True
        st.info("ACM Included in OPP.")

    rhel_value = st.number_input(f"RHEL Guest Value ({sym})", value=800)

# --- CALCULATION ENGINE ---
if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]
        vms_b, cpus_b, ram_b, stg_b = len(data), data['CPUs'].sum(), data['Memory'].sum(), data['Disk_TB'].sum()

        # Efficiencies
        eff_c, eff_r = n_cores * (1-node_overhead/100), n_ram * (1-node_overhead/100)
        rhel_s_b = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * rhel_value

        # 128-Core Entitlement Logic
        subs_per_node = max(1, n_cores / 128)

        # Migration Labor Cost (One-time)
        e_cnt, m_cnt = int(vms_b*(pct_easy/100)), int(vms_b*(pct_med/100))
        h_cnt = vms_b - (e_cnt + m_cnt)
        mig_labor_total = ((e_cnt*hrs_easy) + (m_cnt*hrs_med) + (h_cnt*hrs_hard)) * fte_rate

        # 7-Year Forecasting
        vmw_cum, ocp_cum, table_data = [], [], []
        c_vmw, c_ocp = 0, mig_labor_total

        pricing_map = {
            "OVE (Essentials)": {"b": p_ove, "a": p_acm_v},
            "OKE (Engine)": {"b": p_oke, "a": p_acm_k},
            "OCP (Platform)": {"b": p_ocp, "a": p_acm_k},
            "OPP (Plus)": {"b": p_opp, "a": 0}
        }

        for yr in range(1, horizon + 1):
            g_f = (1 + workload_growth/100)**(yr-1)
            i_f = (1 + sub_inflation/100)**(yr-1)

            # Growth metrics
            v_yr, c_yr, r_yr, s_yr = vms_b*g_f, cpus_b*g_f, (ram_b/1024)*g_f, stg_b*g_f

            # Nodes & Subs
            nodes_yr = int(max((c_yr/cpu_ratio)/eff_c, r_yr/eff_r)) + 1
            subs_yr = nodes_yr * subs_per_node

            # VMware Spend
            vmw_yr = (max(c_yr/cpu_ratio, v_yr*2) * vmw_core_price) + (s_yr * stg_price_tb * 1.2)

            # OpenShift Spend
            base_p = (pricing_map[target_edition]["b"] + (pricing_map[target_edition]["a"] if include_acm else 0)) * i_f
            auto_g = (fte_rate * 12 * 80) * (0.9 if include_acm else 0.4)
            ocp_yr = (subs_yr * base_p) + (s_yr * stg_price_tb) - (rhel_s_b * g_f) - auto_g

            c_vmw += vmw_yr
            c_ocp += ocp_yr
            vmw_cum.append(c_vmw)
            ocp_cum.append(c_ocp)

            table_data.append({
                "Year": f"Year {yr}", "VMs": int(v_yr), "Nodes": nodes_yr, "Subs": subs_yr,
                "Annual VMware": f"{sym}{vmw_yr:,.0f}", "Annual OpenShift": f"{sym}{ocp_yr:,.0f}",
                "Cumulative Savings": f"{sym}{(c_vmw - c_ocp):,.0f}"
            })

        # --- DISPLAY ---
        st.header(f"💼 Business Case Analysis: {cust_name}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Upfront Labor", f"{sym}{mig_labor_total:,.0f}")
        m2.metric(f"Year 1 Nodes", table_data[0]['Nodes'])
        m3.metric(f"Year 1 Subs", table_data[0]['Subs'])
        m4.metric(f"{horizon}-Yr Net Savings", f"{sym}{(c_vmw - c_ocp):,.0f}")

        st.divider()
        st.subheader("Yearly Financial Breakdown")
        st.table(pd.DataFrame(table_data))

        st.divider()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, horizon+1)), y=vmw_cum, name="VMware Baseline", line=dict(color='#6A6E73', dash='dash')))
        fig.add_trace(go.Scatter(x=list(range(1, horizon+1)), y=ocp_cum, name=f"Target: {target_edition}", line=dict(color='#EE0000', width=4)))
        fig.update_layout(title="7-Year Cumulative TCO Projection", yaxis_title=f"Total Spend {sym}")
        st.plotly_chart(fig, use_container_width=True)

        pdf_b = generate_pdf_report(cust_name, {'savings': c_vmw - c_ocp, 'mig_cost': mig_labor_total}, sym, horizon, {'vms': vms_b}, target_edition)
        st.download_button(f"📄 Download {horizon}-Year Executive Proposal", data=pdf_b, file_name=f"V2O_{cust_name}.pdf")
else:
    st.info("👋 Welcome. Please upload an RVTools `vInfo` CSV in the sidebar to begin.")
