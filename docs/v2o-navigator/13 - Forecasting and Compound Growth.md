
## Why Static Sizing Fails
Most migration business cases fail because they assume the data center stays the same size for 5 years. In reality, data grows, VM counts increase, and software prices inflate.

## The Growth Factor
Our tool uses a **Compound Annual Growth Rate (CAGR)** model. 
- If a customer has 100 VMs and 5% growth, by Year 7 they will have ~140 VMs.
- OpenShift nodes are automatically recalculated for each year of the projection to ensure subscription counts remain accurate.

## Subscription Inflation
A standard **10% Year-over-Year (YoY) increase** is applied to the OpenShift list prices. This accounts for standard market price adjustments and allows for a "Worst Case" financial scenario, which builds trust with CFOs.

## The Breakdown Table
This new view allows specialists to show exactly when the "Payback" happens. 
- **Year 1:** Usually shows high OpenShift costs due to migration labor.
- **Year 3-7:** Shows the widening gap (Profitability) as the efficiency of OpenShift handles the growth better than the legacy VMware model.