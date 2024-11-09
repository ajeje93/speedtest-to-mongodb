FROM python:3-slim-buster


RUN apt-get update \
    && apt-get install -y -q --no-install-recommends curl \
    && curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash \
    && apt-get install -y -q --no-install-recommends speedtest \
    && apt-get purge -y curl \
    && apt-get -y autoremove \
    && apt-get clean all \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /config

ADD requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

ADD speedtest.py /

CMD [ "python", "./speedtest.py"]

