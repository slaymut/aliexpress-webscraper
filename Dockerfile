# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# # Install necessary packages and Chrome
# RUN apt-get update && apt-get install -y \
#   wget \
#   gnupg2 \
#   unzip \
#   curl \
#   && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#   && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \

# # Install ChromeDriver
# RUN apt-get update
# RUN apt-get install -yqq unzip
# RUN wget -O https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip
# RUN unzip chromedriver-linux64.zip -d /usr/local/bin/

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