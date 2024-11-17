# Use an official Python runtime as a parent image
FROM python:3.11-slim

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


RUN apt-get update && apt-get install -y ffmpeg

RUN pip install python-multipart newrelic rich
# Set build arguments
ARG SUPABASE_URL
ARG SUPABASE_KEY
ARG SUPABASE_SERVICE_KEY
ARG REPLICATE_API_TOKEN
ARG OPENAI_API_KEY
ARG RAI_GATEWAY_BACKEND_URL
ARG SUPABASE_JWT_SECRET
ARG ZOHO_APP_PASSWORD
ARG NEW_RELIC_LICENSE_KEY
ARG NEW_RELIC_APP_NAME
ARG SENTRY_DSN
ARG APP_ENV
ARG SLACKBOT_RA_WEBHOOK_URL

# Set environment variables
ENV SUPABASE_URL=$SUPABASE_URL \
    SUPABASE_KEY=$SUPABASE_KEY \
    SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY \
    REPLICATE_API_TOKEN=$REPLICATE_API_TOKEN \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    RAI_GATEWAY_BACKEND_URL=$RAI_GATEWAY_BACKEND_URL \
    SUPABASE_JWT_SECRET=$SUPABASE_JWT_SECRET \
    ZOHO_APP_PASSWORD=$ZOHO_APP_PASSWORD \
    SLACKBOT_RA_WEBHOOK_URL=$SLACKBOT_RA_WEBHOOK_URL

ENV NEW_RELIC_LICENSE_KEY=${NEW_RELIC_LICENSE_KEY}
ENV NEW_RELIC_APP_NAME=${NEW_RELIC_APP_NAME}

ENV SENTRY_DSN=${SENTRY_DSN}
ENV APP_ENV=${APP_ENV}


# Copy the rest of the application
COPY . .

# Set the entry point to run New Relic and Uvicorn
ENTRYPOINT ["newrelic-admin", "run-program"]


# Make port 5151 available to the world outside this container
EXPOSE 5151

# Run app.py when the container launches
CMD ["python", "app.py"]