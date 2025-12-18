import pandas as pd
import random

def generate_rvtools_sample(filename="sample_vinfo.csv", num_vms=100):
    """
    Generates a mock RVTools vInfo CSV file with realistic data.
    """

    os_options = [
        "Red Hat Enterprise Linux 7 (64-bit)",
        "Red Hat Enterprise Linux 8 (64-bit)",
        "Microsoft Windows Server 2019 (64-bit)",
        "Microsoft Windows Server 2022 (64-bit)",
        "Ubuntu Linux (64-bit)",
        "Oracle Linux 7 (64-bit)",
        "CentOS 7 (64-bit)"
    ]

    data = []

    for i in range(num_vms):
        # Generate realistic names
        dept = random.choice(["PROD", "DEV", "STAGING", "APP", "DB"])
        vm_name = f"VM-{dept}-{1000 + i:04d}"

        # Sizing: Most VMs are small, some are huge
        cpus = random.choice([2, 4, 8, 16, 32])
        # RAM in MiB (as RVTools does) - using strings with commas to test the parser
        ram_options = [2048, 4096, 8192, 16384, 32768, 65536]
        ram_mib = random.choice(ram_options)
        ram_str = f"{ram_mib:,}"

        os_name = random.choice(os_options)

        data.append({
            "VM": vm_name,
            "Powerstate": "poweredOn",
            "CPUs": cpus,
            "Memory": ram_str,
            "OS according to the configuration file": os_name,
            "DNS Name": f"{vm_name.lower()}.internal.corp",
            "Connection state": "connected",
            "Guest state": "running",
            "Datacenter": "Datacenter-01",
            "Cluster": "Cluster-A"
        })

    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"✅ Success! Generated {num_vms} VMs in '{filename}'")

if __name__ == "__main__":
    generate_rvtools_sample()
