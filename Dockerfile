# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Install necessary packages and Chrome
RUN apt-get update && apt-get install -y \
  wget \
  gnupg2 \
  unzip \
  curl
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

RUN apt-get update && apt-get install -y libpq-dev \
  build-essential \
  postgresql-server-dev-all

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run API_V3.py when the container launches
CMD ["python", "api/API_V3.py"]