# Docker "Official Image" for python
FROM python:3.7-buster

# set the working directory in the container
WORKDIR /api

# copy everything to WORKDIR
ADD . /api

# install the dependencies
RUN pip install -r requirements.txt

# start uWSGI
CMD ["uwsgi", "app.ini"]
