# Use a supported slim image for Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . /app

# Install dependencies
RUN apt update -y && apt install -y awscli && \
    pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["python3", "app.py"]
