FROM ubuntu:trusty

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update && \
    apt-get -y install \
    python3 \
    python3-pip

RUN mkdir -p /tmp
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p $HOME/craigslist
ADD . $HOME/craigslist/
WORKDIR $HOME/craigslist

CMD ["python3", "-u", "craigslist_scraper.py"]