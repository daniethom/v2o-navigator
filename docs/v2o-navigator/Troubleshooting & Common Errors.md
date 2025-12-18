
## TypeError: MarkdownMixin.markdown()
- **Issue:** `got an unexpected keyword argument 'unsafe_allow_none'`
- **Cause:** Typo in the Streamlit `st.markdown` function.
- **Resolution:** Use `unsafe_allow_html=True` when injecting custom CSS styles.

## IndentationError
- **Issue:** `unexpected indent`
- **Cause:** Python is strict about spacing.
- **Resolution:** Ensure all code within an `if` or `with` block is aligned exactly (usually 4 spaces).

## Watchdog Warning
- **Issue:** Streamlit suggests installing Watchdog.
- **Benefit:** Enables "Fast Development Mode" where the app refreshes automatically on save.
- **Fix:** `uv add watchdog`

## Error: ['Total disk capacity MiB'] not in index

### The Cause
RVTools columns often contain trailing spaces or invisible characters (BOM). Additionally, if a script looks for the word `Disk` and the CSV has a column named `Disks` (plural) appearing earlier in the file, the script may incorrectly map the VM's disk count as its storage capacity.

### The Fix
1. **Case-Insensitive Mapping:** We force all column comparisons to lowercase.
2. **Explicit Exclusion:** When searching for storage capacity, we explicitly skip the column named `Disks` to ensure we get the `Total disk capacity MiB` column instead.
3. **Numeric Coercion:** Using `pd.to_numeric(errors='coerce')` ensures that if a cell contains "Unknown" or is empty, the app doesn't crash; it just treats it as 0.

## Error: StreamlitAPIException (Invalid binary data format: bytearray)

### The Cause
The `fpdf2` library outputs PDF data as a `bytearray`. While some Python functions treat `bytearray` and `bytes` similarly, Streamlit's `st.download_button` is a strict interface that expects `bytes` for binary data.

### The Fix
Wrap the PDF output in the `bytes()` constructor before passing it to the download button:
`return bytes(pdf.output())`