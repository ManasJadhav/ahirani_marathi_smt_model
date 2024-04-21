# Use an official Python runtime as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Create a temporary directory
RUN mkdir /tmp/app

# Copy everything from the current directory to the temporary directory
COPY . /tmp/app

# Copy everything from the temporary directory to the container at /app,
# excluding files and directories listed in .dockerignore
RUN cp -r /tmp/app/* . && \
    cp -r /tmp/app/.[^.]* .

# Clean up the temporary directory
RUN rm -rf /tmp/app

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask API
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "api.py"]
