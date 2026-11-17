
# Use a stable Python environment
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Streamlit listens on port 8501
EXPOSE 8501

# Start BusinessDoc AI
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

