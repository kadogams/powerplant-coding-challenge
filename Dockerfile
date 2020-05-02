# Docker "Official Image" for python
FROM python:3.7-buster

RUN apt update -y

# set the working directory in the container
WORKDIR /app

# copy everything to WORKDIR
ADD . /app

# install the dependencies
RUN pip install -r requirements.txt

# start uWSGI
CMD ["uwsgi", "api.ini"]
