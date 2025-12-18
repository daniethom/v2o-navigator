
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