## The Subscription Unit
OpenShift Bare Metal subscriptions are sold in units that cover up to **2 sockets and 128 cores**. 

### Scenarios
1. **Under-density:** A node with 2x 16-core CPUs (32 cores) uses **1 subscription**.
2. **Standard-density:** A node with 2x 64-core CPUs (128 cores) uses **1 subscription**.
3. **Over-density:** A node with 2x 96-core CPUs (192 cores) consumes **1.5 or 2 subscriptions** depending on the specific product terms.

## Why this matters for ROI
When scaling high-core-count servers, OpenShift becomes significantly cheaper than VMware per-core licensing. VMware charges for every core (with a 16-core min per CPU), whereas OpenShift allows you to "fill" the 128-core bucket for a single flat subscription price.