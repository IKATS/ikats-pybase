FROM hub.ops.ikats.org/ubuntu-with-spark
MAINTAINER Germain GAU <germain.gau@c-s.fr>

# TODO: Multi stage build, when buildout will be brutaly slaughtered \o/

RUN apt-get update && \
  apt-get install -y \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    libffi-dev \
    default-jdk \
    scala \
    openssl \
    git \
    libpq-dev

RUN pip3 install --upgrade pip
COPY requirements.txt /tmp
WORKDIR /tmp
RUN pip3 install -r requirements.txt

RUN \
  groupadd \
    -r ikats && \
  useradd \
    -r \
    -g ikats \
    -d /home/ikats \
    -s /sbin/nologin \
    -c "Docker image user" \
    ikats

RUN \
  mkdir /ikats_py_deploy && \
  mkdir /build && \
  mkdir /logs \
  && \
  chown -R ikats:ikats /ikats_py_deploy && \
  chown -R ikats:ikats /build && \
  chown -R ikats:ikats /logs

USER ikats
EXPOSE 8000

ADD . /ikats_py_deploy

WORKDIR /ikats_py_deploy

ENTRYPOINT ["bash", "container_init.sh"]
