
## Why we use generators
In Tech Sales, obtaining a real RVTools file from a customer can take weeks due to security approvals. A generator allows us to:
1. **Demo immediately:** Show the tool's value without waiting for data.
2. **Stress Test:** Generate 10,000 VMs to see how the app performs.
3. **Verify Logic:** Ensure the "RHEL Savings" and "Consolidation" math works with known inputs.

## The Script Logic
The `generate_sample_data.py` script mimics the **RVTools v10.x** schema. 
- It uses the column name `OS according to the configuration file`.
- It formats the `Memory` column with commas (e.g., `8,192`) to ensure our parser's cleaning logic is working correctly.
- It includes a randomized mix of Windows and Linux to test the complexity and effort calculations.

## How to use
Run `uv run generate_sample_data.py`. This outputs `sample_vinfo.csv`, which is excluded from Git (if using a .gitignore) to keep the repo clean.