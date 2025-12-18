# Module 4: Partner Storage & Solution Mapping

## Why Storage Matters in TCO
In a VMware environment, storage is often a "black box" (vSAN or a SAN array). When moving to OpenShift, customers need to decide how to handle **Persistent Volumes (PVs)**.

## The Options in our Tool
1. **OpenShift Data Foundation (ODF):** - Software-defined storage based on Ceph.
   - *Value Prop:* Single support ticket for the whole stack. Highly scalable.
2. **NetApp Trident:** - CSI driver for existing NetApp arrays.
   - *Value Prop:* Allows customers to sweat their existing hardware assets.
3. **Portworx:** - Enterprise-grade storage for Kubernetes.
   - *Value Prop:* Advanced DR/Backup features often required for mission-critical databases.

## How the Tool Maps These
Currently, the tool uses the selection to identify the architectural target. In future versions, we can add "Storage Surcharge" logic to calculate the exact cost difference between ODF and third-party licenses.

## Why Advanced Cluster Management (ACM)?
You mentioned ACM is a requirement. In the tool, ACM is mapped to the **OPP (Platform Plus)** edition. When showing ROI, remind the customer that ACM reduces "Day 2" operational costs by providing a single pane of glass for all clusters.