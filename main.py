import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="V2O Navigator", page_icon="🚀")

# 2. The Header
st.title("V2O Navigator")
st.subheader("VMware to OpenShift TCO & ROI Calculator")

# 3. Sidebar for Customer Information
with st.sidebar:
    st.header("Customer Profile")
    customer_name = st.text_input("Customer Name", "Acme Corp")
    vmware_annual_cost = st.number_input("Current Annual VMware Spend ($)", value=50000)

# 4. The Logic: Mapping VMware to OpenShift
st.write(f"### Analysis for {customer_name}")

# Let's create a simple calculation:
# Usually, moving to OpenShift (OCP) with ACM reduces OpEx by ~30%
ocp_savings_multiplier = 0.70
calculated_savings = vmware_annual_cost * (1 - ocp_savings_multiplier)

# 5. Display the ROI Metrics
col1, col2 = st.columns(2)
col1.metric("Current VMware TCO (Annual)", f"${vmware_annual_cost:,}")
col2.metric("OpenShift Estimated TCO", f"${int(vmware_annual_cost * ocp_savings_multiplier):,}")

st.success(f"Potential Annual Saving: ${int(calculated_savings):,}")

# 6. Future Feature Placeholder
st.info("Next Step: Upload RVTools CSV to map specific CPU/RAM workloads.")
