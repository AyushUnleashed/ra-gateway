# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Combine with system dependencies installation and cleanup in one RUN command
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install python-multipart
# Set build arguments
ARG SUPABASE_URL
ARG SUPABASE_KEY
ARG SUPABASE_SERVICE_KEY
ARG REPLICATE_API_TOKEN
ARG OPENAI_API_KEY
ARG RAI_GATEWAY_BACKEND_URL
ARG SUPABASE_JWT_SECRET
ARG ZOHO_APP_PASSWORD

# Set environment variables
ENV SUPABASE_URL=$SUPABASE_URL \
    SUPABASE_KEY=$SUPABASE_KEY \
    SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY \
    REPLICATE_API_TOKEN=$REPLICATE_API_TOKEN \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    RAI_GATEWAY_BACKEND_URL=$RAI_GATEWAY_BACKEND_URL \
    SUPABASE_JWT_SECRET=$SUPABASE_JWT_SECRET \
    ZOHO_APP_PASSWORD=$ZOHO_APP_PASSWORD

# Copy the rest of the application
COPY . .

# Make port 5151 available to the world outside this container
EXPOSE 5151

# Run app.py when the container launches
CMD ["python", "app.py"]