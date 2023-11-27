# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y \
        curl \
        chromium \
        chromium-driver \
        libglib2.0-0 \
        libnss3 \
        libgconf-2-4 \
        libfontconfig1 \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome and GnuPG tools
RUN apt-get update && \
    apt-get install -y gnupg gnupg1 gnupg2 && \
    curl -sSL https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 3002 available to the world outside this container
EXPOSE 3002

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "api.py"]
