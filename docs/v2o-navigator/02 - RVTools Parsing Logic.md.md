

## Why RVTools?
RVTools is the industry standard for VMware inventory. For an OpenShift Tech Sales specialist, it provides the "Ground Truth" needed to size a cluster and calculate ROI.

## How the Parser Works
The app uses the **Pandas** library (the gold standard for data in Python) to perform three main tasks:

1. **Cleaning:** It strips hidden spaces from CSV headers (a common issue with CSV exports).
2. **Aggregation:** It sums up the `CPUs` and `Memory` columns to determine the total footprint.
3. **Pattern Matching:** It uses "Regular Expressions" (Regex) to scan the OS column for strings like "Red Hat" or "RHEL".

## Key Columns Used
- `VM`: Name of the virtual machine.
- `CPUs`: Used to calculate OpenShift Core requirements.
- `Memory`: Used to calculate Node RAM requirements.
- `OS according to the configuration`: Used to identify "RHEL Savings" opportunities.

## Training Exercise
1. Export a `vInfo` tab from RVTools as a CSV.
2. Upload it to the Navigator.
3. Verify that the "Total RAM" metric matches the "Memory" total in your Excel version of the report.

## Dealing with "Dirty" Data
In technical sales, customer data is rarely perfect. Our parser handles two common "dirty data" issues:

### 1. Schema Drift (Column Names)
RVTools versions change. One version might say `OS according to the configuration`, while another says `OS according to the configuration file`.
- **The Solution:** Our script uses a "Fuzzy Search" logic to look for keywords like "OS" or "Memory" if the exact match fails.

### 2. Locale Formatting (The Comma Problem)
Excel often exports numbers with commas (e.g., `1,024`). Python sees this as a **String (Text)**, not a **Float (Number)**. 
- **The Logic:** We must strip the commas using `.str.replace(',', '')` before converting the column to a number. 
- **Why it matters:** Without this, you cannot sum the total RAM or CPUs; Python will simply throw an error.

### 3. MB to GB Conversion
RVTools reports memory in **MiB**. Since OpenShift nodes are usually sized in **GB**, we divide the total by `1024` to provide a metric that is relevant to our platform.

## Capturing the Full Stack
To move from "Demo" to "Real-World," we now extract the storage footprint in addition to Compute and RAM.

### Key Column: Total disk capacity MiB
RVTools reports storage in **MiB (Mebibytes)**. To make this relevant for modern storage arrays and cloud pricing, our parser performs the following:
1. **Cleaning:** Removes commas from the string.
2. **Conversion:** Divides by `1,048,576` (1024 * 1024) to convert MiB to **Terabytes (TB)**.

## Why TB matters
Sizing **OpenShift Data Foundation (ODF)** or Partner solutions like **NetApp Trident** requires an accurate TB count to determine the number of disks or licenses needed.

### Updated Logic Check
- **VM Name:** Identifies the workload.
- **CPUs/Memory:** Sizes the Compute nodes.
- **Disk_MiB:** Sizes the Storage layer.
- **OS:** Calculates the RHEL Dividend.