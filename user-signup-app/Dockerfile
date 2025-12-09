FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates templates/

# Create data directory for SQLite database
RUN mkdir -p /data

# Expose port
EXPOSE 8080

# Set environment variables with defaults
ENV CLUSTER_DOMAIN=example.com
ENV USER_PASSWORD=changeme
ENV MAX_USERS=25
ENV LAB_INSTRUCTIONS_URL=https://rhoai-genaiops.github.io/lab-instructions/
ENV DB_PATH=/data/users.db
ENV ADMIN_TOKEN=admin-secret-token-change-me

# Run the application
CMD ["python", "app.py"]
