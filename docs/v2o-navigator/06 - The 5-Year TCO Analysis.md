
## Why 5 Years?
In Enterprise Sales, a 1-year view is never enough. The first year of a migration always looks expensive because of the **"Migration Double-Bubble"** (paying for the old and new platforms simultaneously) and the labor cost of moving data.

## Key Components of our TCO Model
1. **VMware Baseline:** We assume a flat renewal cost. In reality, with Broadcom's changes, this might actually be an upward curve (you can add an 'Inflation' slider in v2.0!).
2. **The Migration Spike:** Year 1 includes the one-time engineering cost to move VMs and containerize apps.
3. **The OpEx Drop:** This is where OpenShift wins. Because of **ACM** and **RHEL Savings**, the "Slope" of the OpenShift line is much flatter than VMware.
4. **The Breakeven Point:** The moment the green line crosses the red line. For most OpenShift customers, this happens between **Month 18 and Month 30**.

## Teaching the "ROI Conversation"
- **Hard ROI:** License reduction (VMware vs OpenShift).
- **Operational ROI:** Reclaiming thousands of engineering hours (FTE redirection).
- **Business ROI:** Getting apps to production faster (not calculated in this tool, but a key talking point).

## Training Exercise
Modify the `ocp_sub_cost` in the sidebar and observe how the Payback Period changes. If the customer has high RHEL usage, the payback period should move earlier (Year 2).