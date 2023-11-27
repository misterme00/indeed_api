# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y xvfb



# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Upgrade pip
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Install any needed packages specified in requirements.txt
# RUN python -m pip install --no-cache-dir flask>=2.0 selenium==4.0.0 beautifulsoup4==4.10.0 pyvirtualdisplay==2.2 Werkzeug==0.16.1

# Make port 3002 available to the world outside this container
EXPOSE 3002

# Run app.py when the container launches
CMD ["python", "api.py"]