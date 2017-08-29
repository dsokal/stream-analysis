FROM python:3.6.2-alpine3.6

WORKDIR /docker/app

# Install system dependencies
RUN apk add --update --no-cache make gcc g++ nodejs nodejs-npm

# Install pip dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Install supervisor (nodejs package)
RUN npm install supervisor -g
