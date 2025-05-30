# Use a Python base image
FROM python:3.9-slim-buster

# Copy the application code into the container
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install confluent-kafka

# Command to run the script
CMD ["python", "traffic_publisher.py"]