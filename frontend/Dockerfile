# Use a Python base image
FROM python:3.9-slim-buster

# Copy the application code into the container
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install confluent-kafka

# Install dependencies
RUN pip install flask requests

# Command to run the application
# This will start the Flask application.
CMD ["python", "app.py"]
