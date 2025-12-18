import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- INITIAL SETUP ---
st.set_page_config(page_title="V2O Navigator", layout="wide", page_icon="🚀")

# --- PDF GENERATION FUNCTION ---
def create_pdf(customer, vms, cpus, ram, savings, nodes, edition, total_savings):
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "V2O Navigator: Migration Report", ln=True, align="C")

    # Customer Info
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Prepared for: {customer}", ln=True)
    pdf.ln(5)

    # Summary Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Current Infrastructure Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Total Virtual Machines: {vms}", ln=True)
    pdf.cell(0, 10, f"- Total vCPU Count: {cpus}", ln=True)
    pdf.cell(0, 10, f"- Total RAM: {ram:,.0f} GB", ln=True)

    # Financials
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Financial Impact", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Estimated Annual Guest OS Savings: ${savings:,.0f}", ln=True)
    pdf.cell(0, 10, f"- Project 5-Year Net Savings: ${total_savings:,.0f}", ln=True)

    # Architecture
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Proposed Architecture", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"- Target Platform Edition: {edition}", ln=True)
    pdf.cell(0, 10, f"- Recommended Worker Nodes (N+1): {nodes}", ln=True)

    # Disclaimer
    pdf.ln(20)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Disclaimer: This report is an estimate based on industry averages and provided data. Actual costs and sizing may vary based on final configuration and enterprise agreements.")

    return pdf.output(dest='S')

# --- REUSE PREVIOUS PARSER & UI LOGIC ---
# (I am keeping the core logic but adding the download button at the end)

def process_rvtools(file):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        mapping = {'VM': 'VM', 'CPUs': 'CPUs', 'Memory': 'Memory', 'OS': 'OS according to the configuration file'}
        for key, expected in mapping.items():
            if expected not in df.columns:
                found = [col for col in df.columns if key in col]
                if found: mapping[key] = found[0]
                else: return None
        df = df[[mapping['VM'], mapping['CPUs'], mapping['Memory'], mapping['OS']]]
        df.columns = ['VM', 'CPUs', 'Memory', 'OS']
        for col in ['CPUs', 'Memory']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)
        return df
    except: return None

# --- SIDEBAR & MAIN APP ---
with st.sidebar:
    st.title("V2O Navigator")
    customer_name = st.text_input("Customer Name", "Acme Corp")
    uploaded_file = st.file_uploader("Upload RVTools vInfo CSV", type=["csv"])
    cpu_ratio = st.slider("vCPU Consolidation", 1.0, 6.0, 3.0)
    node_type = st.selectbox("Node Size", ["Standard (16 vCPU | 64GB RAM)", "Large (32 vCPU | 128GB RAM)"])
    edition = st.selectbox("Edition", ["OVE", "OKE", "OCP", "OPP"])
    annual_vmw_cost = st.number_input("Annual VMware Spend ($)", value=100000)

if uploaded_file:
    data = process_rvtools(uploaded_file)
    if data is not None:
        # Calculations
        total_vms = len(data)
        total_cpus = data['CPUs'].sum()
        total_ram_gb = data['Memory'].sum() / 1024
        num_rhel = len(data[data['OS'].str.contains("Red Hat|RHEL", case=False, na=False)])
        rhel_savings = num_rhel * 800

        n_cores, n_ram = (16, 64) if "Standard" in node_type else (32, 128)
        worker_nodes = int(max((total_cpus/cpu_ratio)/n_cores, total_ram_gb/n_ram)) + 1

        # Financials for TCO
        ocp_total_5yr = (worker_nodes * 2500 * 5) - (rhel_savings * 5)
        vmw_total_5yr = annual_vmw_cost * 5
        net_5yr_savings = vmw_total_5yr - ocp_total_5yr

        # Display Metrics
        st.header(f"Analysis for {customer_name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total VMs", total_vms)
        c2.metric("Worker Nodes", worker_nodes)
        c3.metric("5-Year Savings", f"${net_5yr_savings:,.0f}")

        # --- PDF DOWNLOAD BUTTON ---
        st.divider()
        pdf_data = create_pdf(customer_name, total_vms, total_cpus, total_ram_gb, rhel_savings, worker_nodes, edition, net_5yr_savings)

        st.download_button(
            label="📄 Download Executive TCO Report (PDF)",
            data=pdf_data,
            file_name=f"V2O_Report_{customer_name}.pdf",
            mime="application/pdf"
        )
else:
    st.info("Please upload data to begin.")
