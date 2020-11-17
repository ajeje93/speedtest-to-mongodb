FROM python:3-slim-buster

ADD requirements.txt /

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
    && apt-get update \
    && apt-get install -y -q --no-install-recommends gnupg1 apt-transport-https dirmngr lsb-release \
    && export INSTALL_KEY=379CE192D401AB61 \
    && export DEB_DISTRO=$(lsb_release -sc) \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $INSTALL_KEY \
    && echo "deb https://ookla.bintray.com/debian ${DEB_DISTRO} main" | tee /etc/apt/sources.list.d/speedtest.list \
    && apt-get update \
    && apt-get install -y -q --no-install-recommends speedtest \
    && apt-get clean all \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir /config

ADD speedtest.py /
ADD timeout.py /

CMD [ "python", "./speedtest.py"]

