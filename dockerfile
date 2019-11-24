FROM python:3.7-alpine

MAINTAINER Subhayan Bhattacharya

ENV PYTHONUNBUFFERED 1

COPY Pipfile* /tmp/

RUN cd /tmp && pip install pipenv && pipenv lock --requirements > requirements.txt

RUN pip install -r /tmp/requirements.txt

RUN mkdir /app

WORKDIR /app

COPY ./app /app

RUN adduser -D user
USER user




