## The Worker Node Anatomy
In OpenShift, a worker node's capacity is not 100% available for user workloads. We must account for:
1. **Kubelet / OS Reserved:** Essential services to keep the node healthy.
2. **Eviction Thresholds:** Memory reserved to prevent the node from crashing under pressure.

## Calculation Logic
Our tool calculates **Effective Capacity**:
`Effective Cores = Physical Cores * (1 - Overhead %)`

This ensures that when we calculate the number of nodes needed to support 2,000 vCPUs, we don't under-size the cluster. 

## Custom Hardware (BOM)
Customers often have "Preferred Server Specs" (e.g., Dell PowerEdge or HP ProLiant). The **Custom Spec** option allows the specialist to input the exact core and RAM counts of the customer's hardware to provide a "Bespoke" sizing report.