FROM python:3.9

WORKDIR /app

# Install postgresql-client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN adduser --disabled-password --gecos '' app_user

# Copy the entire application
COPY . .

# Copy entrypoint.sh and make it executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Set proper permissions
RUN chown -R app_user:app_user /app

# Create migrations directory if it doesn't exist
RUN mkdir -p migrations && chown -R app_user:app_user migrations

# Switch to non-root user
USER app_user

# Use CMD instead of ENTRYPOINT
CMD ["/bin/sh", "/app/entrypoint.sh"]
