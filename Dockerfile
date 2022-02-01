# Pull base image
FROM python:3.9.7-bullseye
# Set environment variables
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
# Install Linux Packages
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install nano
# Set work directory
WORKDIR /drf
# Install dependencies
COPY Pipfile Pipfile.lock /drf/
RUN pip install pipenv && pipenv install --system
# Copy project
COPY . /drf/