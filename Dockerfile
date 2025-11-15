# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for some Python packages
# For example, if you use `psycopg2` or `mysqlclient`, you might need `build-essential`
# and database client libraries. For `firestore`, no specific system deps are usually needed.
# If you find issues with specific packages, add their system dependencies here.
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     # libpq-dev \ # Example for psycopg2
#     # default-libmysqlclient-dev \ # Example for mysqlclient
#     && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the uvicorn server when the container launches
# Use 0.0.0.0 to bind to all network interfaces
# The --port is set to 8000, which matches the EXPOSE instruction
ENV PORT 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
