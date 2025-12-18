
## The Market Shift
Legacy VMware pricing (Per-Socket/Per-VM) has been replaced by **Per-Core Subscriptions**. Customers now face two main paths:
1. **VCF (VMware Cloud Foundation):** The full software-defined stack.
2. **VVF (vSphere Foundation):** A more basic virtualization offering.



## How our Tool Calculates the Baseline
Since we don't know the customer's physical hardware exactly from a VM-level RVTools export, we estimate **Physical Cores** using the following "Specialist Logic":

$$Estimated Cores = \max\left(\frac{Total vCPUs}{Consolidation Ratio}, Total VMs \times 2\right)$$

### Why the "2 Cores per VM" Floor?
Most modern licensing models have a minimum core count per server/VM. Using this "floor" ensures we don't under-estimate the customer's current spend, providing a more realistic "As-Is" baseline.

## Comparing Storage TCO
We assume legacy storage is roughly **20% more expensive** to maintain than modern Software Defined Storage (SDS). The tool applies this "Legacy Tax" to the VMware baseline to show the efficiency of moving to a unified platform.