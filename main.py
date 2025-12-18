import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# --- INITIAL SETUP & THEMING ---
st.set_page_config(
    page_title="V2O Navigator | Migration ROI",
    page_icon="🚀",
    layout="wide"
)

# Custom Red Hat-inspired styling
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

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.date.today()}', 0, 0, 'C')

def generate_pdf_report(cust_name, metrics, financials, nodes, edition, acm_included):
    pdf = ROIPDF()
    pdf.add_page()

    # Executive Summary
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Executive Summary for {cust_name}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    acm_text = " (with ACM)" if acm_included else ""
    pdf.multi_cell(0, 10, f"This report outlines the technical and financial impact of migrating from a legacy virtualization estate to an enterprise container platform: {edition}{acm_text}.")
    pdf.ln(5)

    # Summary Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "Current Inventory Metrics", border=1)
    pdf.cell(95, 10, "Target Architecture", border=1, ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(95, 10, f"Total VMs: {metrics['vms']}", border=1)
    pdf.cell(95, 10, f"Target Nodes: {nodes}", border=1, ln=True)
    pdf.cell(95, 10, f"Total vCPUs: {metrics['cpus']}", border=1)
    pdf.cell(95, 10, f"Edition: {edition}", border=1, ln=True)
    pdf.cell(95, 10, f"Total Storage: {metrics['storage_tb']:.2f} TB", border=1)
    pdf.cell(95, 10, f"ACM Included: {'Yes' if acm_included else 'No'}", border=1, ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Financial Projection (5-Year Forecast)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Projected Net Savings: ${financials['savings']:,.0f}", ln=True)
    pdf.cell(0, 10, f"- Est. Annual Licensing Reduction: ${financials['licensing_red']:,.0f}", ln=True)

    return bytes(pdf.output())

# --- RESILIENT DATA PROCESSING ---

def process_rvtools(file):
    try:
        df = pd.read_csv(file)
        df.columns = [str(c).strip() for c in df.columns]

        mapping = {}
        mapping['VM'] = next((c for c in df.columns if c.lower() in ['vm', 'virtual machine']), None)
        mapping['CPUs'] = next((c for c in df.columns if c.lower() in ['cpus', 'vcpu']), None)
        mapping['Memory'] = next((c for c in df.columns if 'memory' in c.lower()), None)
        mapping['OS'] = next((c for c in df.columns if 'os according to' in c.lower() or c.lower() == 'os'), None)
        mapping['Disk'] = next((c for c in df.columns if ('capacity' in c.lower() or 'mib' in c.lower()) and 'disk' in c.lower()), None)

        for key, value in mapping.items():
            if value is None:
                st.error(f"❌ Could not find a reliable column for **{key}**.")
                return None

        df_clean = df[[mapping['VM'], mapping['CPUs'], mapping['Memory'], mapping['OS'], mapping['Disk']]].copy()
        df_clean.columns = ['VM', 'CPUs', 'Memory', 'OS', 'Disk_MiB']

        for col in ['CPUs', 'Memory', 'Disk_MiB']:
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '').replace('nan', '0')
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)

        df_clean['Disk_TB'] = df_clean['Disk_MiB'] / 1048576
        return df_clean
    except Exception as e:
        st.error(f"⚠️ Error processing CSV: {e}")
        return None

# --- SIDEBAR: INPUTS & PRICING ---

with st.sidebar:
    st.image("https://www.redhat.com/cms/managed-files/Logo-RedHat-OpenShift-A-Standard-RGB.png", width=200)
    st.title("V2O Navigator")

    uploaded_file = st.file_uploader("Upload RVTools vInfo CSV", type=["csv"])

    st.divider()
    st.header("1. Sizing Assumptions")
    cpu_ratio = st.slider("Consolidation Ratio (vCPU:Core)", 1.0, 6.0, 3.0)
    node_size = st.selectbox("Node Instance", ["Standard (16c/64g)", "Large (32c/128g)", "Extra Large (64c/256g)"])

    st.divider()
    st.header("2. VMware & Storage Costing")
    vmw_model = st.selectbox("VMware Model", ["VCF (Subscription)", "VVF (Subscription)", "Legacy ELA"])
    vmw_core_price = st.number_input(f"Annual {vmw_model} Price / Core ($)", value=350)
    stg_price_tb = st.number_input("Annual Storage Price / TB ($)", value=150)

    st.divider()
    st.header("3. OpenShift & ACM Pricing")
    with st.expander("Adjust Edition Pricing"):
        price_ove = st.number_input("OVE (Essentials) Price", value=1500)
        price_oke = st.number_input("OKE (Engine) Price", value=2200)
        price_ocp = st.number_input("OCP (Platform) Price", value=3200)
        price_opp = st.number_input("OPP (Plus) Price", value=4800)
        st.caption("ACM Add-ons")
        price_acm_virt = st.number_input("ACM for Virtualization (Add-on)", value=600)
        price_acm_k8s = st.number_input("ACM for Kubernetes (Add-on)", value=900)

    target_edition = st.selectbox("Proposed Edition", ["OVE (Essentials)", "OKE (Engine)", "OCP (Platform)", "OPP (Plus)"])

    # ACM Toggles
    include_acm = False
    if "OVE" in target_edition:
        include_acm = st.checkbox("Add ACM for Virtualization?")
    elif "OKE" in target_edition or "OCP" in target_edition:
        include_acm = st.checkbox("Add ACM for Kubernetes?")
    elif "OPP" in target_edition:
        st.info("ACM is already included in Platform Plus (OPP).")
        include_acm = True

    st.divider()
    st.header("4. Labor & Efficiency")
    fte_rate = st.number_input("FTE Hourly Rate ($)", value=80)
    rhel_list_price = st.number_input("RHEL Guest Value ($)", value=800)

# --- MAIN APP LOGIC ---

if uploaded_file:
    data = process_rvtools(uploaded_file)

    if data is not None:
        cust_name = uploaded_file.name.split('.')[0]

        # A. Summary Metrics
        total_vms, total_vcpus = len(data), data['CPUs'].sum()
        total_ram_gb = data['Memory'].sum() / 1024
        total_disk_tb = data['Disk_TB'].sum()

        st.header(f"📊 Infrastructure Summary: {cust_name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total VMs", total_vms)
        c2.metric("Total vCPUs", int(total_vcpus))
        c3.metric("Total RAM (GB)", f"{total_ram_gb:,.0f}")
        c4.metric("Total Storage (TB)", f"{total_disk_tb:,.1f}")

        # B. Financial Baseline (VMware)
        est_physical_cores = max(total_vcpus / cpu_ratio, total_vms * 2)
        annual_vmw_licensing = est_physical_cores * vmw_core_price
        annual_vmw_storage = total_disk_tb * (stg_price_tb * 1.2)
        vmw_annual_tco = annual_vmw_licensing + annual_vmw_storage

        # C. Target Architecture Sizing
        n_cores, n_ram = (16, 64) if "Standard" in node_size else (32, 128) if "Large" in node_size else (64, 256)
        req_nodes = int(max((total_vcpus/cpu_ratio)/n_cores, total_ram_gb/n_ram)) + 1

        # D. RHEL Savings & Multi-Edition Comparison
        st.divider()
        st.header("⚖️ Platform Edition Comparison (Base vs +ACM)")
        rhel_savings = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)]) * rhel_list_price

        comparison = []
        pricing_map = {
            "OVE (Essentials)": {"base": price_ove, "acm": price_acm_virt},
            "OKE (Engine)": {"base": price_oke, "acm": price_acm_k8s},
            "OCP (Platform)": {"base": price_ocp, "acm": price_acm_k8s},
            "OPP (Plus)": {"base": price_opp, "acm": 0} # Included
        }

        for ed, prices in pricing_map.items():
            base_annual = req_nodes * prices['base']
            acm_annual = req_nodes * prices['acm']

            # Efficiency logic: ACM significantly improves automation ROI
            efficiency_gain = 0.9 if (prices['acm'] > 0 or "Plus" in ed) else 0.4
            hrly_savings = (fte_rate * 12 * 80) * efficiency_gain

            # Logic to show the selected configuration impact
            total_sub = base_annual + (acm_annual if (include_acm and ed in target_edition) or "Plus" in ed else 0)
            net_impact = total_sub - rhel_savings - hrly_savings

            comparison.append({
                "Edition": ed,
                "Base Subscription": f"${base_annual:,.0f}",
                "ACM Add-on Cost": f"${acm_annual:,.0f}" if prices['acm'] > 0 else "Included",
                "Net Annual Impact": f"${int(net_impact):,}"
            })
        st.table(pd.DataFrame(comparison))

        # E. 5-Year Cumulative TCO Projection
        st.divider()
        st.header("📈 5-Year Cumulative TCO Projection")

        # Calculate selected subscription annual cost including ACM if toggled
        selected_base_price = pricing_map[target_edition]['base']
        selected_acm_price = pricing_map[target_edition]['acm'] if include_acm else 0
        selected_sub_annual = req_nodes * (selected_base_price + selected_acm_price)

        selected_stg_annual = total_disk_tb * stg_price_tb

        vmw_5yr = [vmw_annual_tco * i for i in range(1, 6)]
        ocp_5yr = []
        current_ocp = (total_vms * 8 * fte_rate)

        for i in range(1, 6):
            current_ocp += (selected_sub_annual + selected_stg_annual - rhel_savings)
            ocp_5yr.append(current_ocp)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=vmw_5yr, name="Current VMware (Estimated)", line=dict(color='#6A6E73', width=2, dash='dash')))
        fig.add_trace(go.Scatter(x=[1,2,3,4,5], y=ocp_5yr, name=f"Target {target_edition} {'+ ACM' if include_acm and 'Plus' not in target_edition else ''}", line=dict(color='#EE0000', width=4)))
        fig.update_layout(xaxis_title="Year", yaxis_title="Total Spend ($)")
        st.plotly_chart(fig, use_container_width=True)

        # F. Export to PDF
        st.divider()
        m_dict = {'vms': total_vms, 'cpus': int(total_vcpus), 'storage_tb': total_disk_tb, 'ratio': cpu_ratio}
        f_dict = {'savings': vmw_5yr[-1] - ocp_5yr[-1], 'licensing_red': annual_vmw_licensing - selected_sub_annual}

        pdf_bytes = generate_pdf_report(cust_name, m_dict, f_dict, req_nodes, target_edition, include_acm)

        st.download_button(
            label="📄 Download Detailed Executive Report",
            data=pdf_bytes,
            file_name=f"V2O_Navigator_{cust_name}.pdf",
            mime="application/pdf"
        )
else:
    st.info("👋 **Welcome.** Please upload an RVTools `vInfo` CSV in the sidebar to begin.")
