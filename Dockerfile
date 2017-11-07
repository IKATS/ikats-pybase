FROM python:3.6

MAINTAINER Germain GAU <germain.gau@c-s.fr>

ARG http_proxy=""
ARG https_proxy=""

RUN groupadd -r ikats &&\
useradd -r -g ikats -d /home/ikats -s /sbin/nologin -c "Docker image user" ikats

# Set the proxies for apt
RUN (test -z "$http_proxy" || echo "Acquire::http::Proxy \"$http_proxy\";" >> /etc/apt/apt.conf) && \
    (test -z "$https_proxy" || echo "Acquire::https::Proxy \"$https_proxy\";" >> /etc/apt/apt.conf)

RUN apt update \
  && apt install -y \
    libffi-dev \
    libatlas-base-dev \
    libblas-dev \
    liblapack-dev \
    liblapack3 \
    liblapacke \
    liblapacke-dev \
  && apt-get clean

RUN \
  mkdir /ikats_py_deploy && \
  mkdir /build && \
  mkdir /logs && \
  chown -R ikats /ikats_py_deploy && \
  chown -R ikats /build && \
  chown -R ikats /logs

USER ikats
EXPOSE 8000

ADD . /ikats_py_deploy

WORKDIR /ikats_py_deploy/docker

CMD ["bash", "container_init.sh"]
