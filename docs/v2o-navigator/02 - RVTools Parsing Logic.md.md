# Module 2: RVTools Parsing Logic

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