# Docker "Official Image" for python
FROM python:3.7-buster

RUN apt-get update -y

# set the working directory in the container
WORKDIR /app

# copy everything to WORKDIR
ADD . /app

# create directory for the log file specified in api.ini
RUN mkdir -p /var/log/uwsgi

# install the dependencies
RUN pip install -r requirements.txt

# start uWSGI
CMD ["uwsgi", "api.ini"]
