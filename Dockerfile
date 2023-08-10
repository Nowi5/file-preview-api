FROM python:3.10-slim

ENV PATH /usr/local/bin:$PATH
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED=True \
    APP_HOME=/app \
    PORT=5000

WORKDIR $APP_HOME

COPY . ./

RUN apt-get update && apt-get install -y apt-utils
RUN apt-get install -yqq wget unzip curl nano
    
RUN apt-get purge -y --auto-remove ca-certificates wget

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       wget \
       libreoffice \
       default-jre \
       libreoffice-java-common \
    && rm -rf /var/lib/apt/lists/*
RUN	apt-get libreoffice --version

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install unoserver in libreoffice phyton version
RUN pip install virtualenv
RUN mkdir /environments
RUN virtualenv --python=/usr/bin/python3 --system-site-packages /environments/virtenv
RUN /environments/virtenv/bin/pip install unoserver

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
