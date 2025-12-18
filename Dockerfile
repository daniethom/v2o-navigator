# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install 'uv' for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 4. Copy your dependency files first (optimizes caching)
COPY pyproject.toml uv.lock ./

# 5. Install dependencies into a system-wide environment
RUN uv pip install --system -r pyproject.toml

# 6. Copy the rest of your application code
COPY . .

# 7. Expose the port Streamlit runs on
EXPOSE 8501

# 8. Command to run the app when the container starts
# We add --server.address 0.0.0.0 so it listens to all network traffic
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
