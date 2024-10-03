# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

ADD requirements.txt /app/requirements.txt

# Set environment variables needed during build
ARG SUPABASE_URL
ARG SUPABASE_KEY
ARG SUPABASE_SERVICE_KEY
ARG REPLICATE_API_TOKEN
ARG OPENAI_API_KEY
ARG RAI_GATEWAY_BACKEND_URL
ARG SUPABASE_JWT_SECRET

# Set environment variables in the app
ENV SUPABASE_URL=$SUPABASE_URL
ENV SUPABASE_KEY=$SUPABASE_KEY
ENV SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY
ENV REPLICATE_API_TOKEN=$REPLICATE_API_TOKEN
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV RAI_GATEWAY_BACKEND_URL=$RAI_GATEWAY_BACKEND_URL
ENV SUPABASE_JWT_SECRET=$SUPABASE_JWT_SECRET

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD . /app/

# Make port 5151 available to the world outside this container
EXPOSE 5151

# Run app.py when the container launches
CMD ["python", "app.py"]