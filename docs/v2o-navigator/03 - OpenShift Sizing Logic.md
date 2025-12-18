

## The "Density Dividend"
The biggest driver of ROI when moving from VMware to OpenShift is **Density**. 

### 1. vCPU Consolidation Ratio
In a typical VMware environment, vCPUs are over-committed. 
- **Conservative:** 2:1 (2 VM vCPUs for every 1 Physical Core)
- **Standard:** 3:1 or 4:1
- **Aggressive:** 6:1 (For Dev/Test workloads)

Our tool uses a slider to let the customer see how increasing density reduces the number of physical nodes (and therefore the OpenShift subscription cost).

### 2. The "Bottleneck" Calculation
A cluster is usually constrained by either **Compute (CPU)** or **Memory (RAM)**.
- **CPU Bound:** You run out of cores before you run out of RAM.
- **RAM Bound:** You run out of RAM before you run out of cores.

Our logic uses `max(nodes_by_cpu, nodes_by_ram)` to ensure the cluster is sized for the most demanding resource.

## Redundancy (N+1)
We always add **+1 node** to the calculation. This ensures that if one physical server fails, the OpenShift scheduler can move the workloads to the remaining nodes without a performance hit.

## The 3-Node Control Plane
In addition to the worker nodes calculated from RVTools, every production OpenShift cluster requires **3 Control Plane (Master) nodes** for the "brains" of the operations.