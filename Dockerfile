FROM python:3-slim-buster

ADD requirements.txt /

RUN apt-get update \
    && apt-get install -y -q --no-install-recommends curl \
    && curl -s https://install.speedtest.net/app/cli/install.deb.sh | bash \
    && apt-get install -y -q --no-install-recommends speedtest \
    && apt-get purge -y curl \
    && apt-get -y autoremove \
    && apt-get clean all \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir /config

ADD speedtest.py /
ADD timeout.py /

CMD [ "python", "./speedtest.py"]

