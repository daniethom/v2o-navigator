
This project uses a modern, high-performance stack for rapid prototyping.

## 1. Python & `uv`
- **Why `uv`?** It replaces `pip`. It is written in Rust and is 10x-100x faster. It handles virtual environments automatically.
- **Command used:** `uv add streamlit pandas`

## 2. Streamlit
- **Purpose:** A frontend framework that allows us to build web apps using only Python. No HTML/CSS/JavaScript knowledge required.
- **Role in TechSales:** Allows us to build custom calculators for customers in minutes, not days.

## 3. Git & GitHub
- **Workflow:** Code is stored on GitHub for version control and collaboration.
- **Authentication:** Uses Personal Access Tokens (PAT) instead of passwords for security.