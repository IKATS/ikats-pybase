FROM ubuntu:xenial
MAINTAINER Germain GAU <germain.gau@c-s.fr>

# TODO: Move the ADD below in another image, and rebase this Dockerfile on it.
# (Because caching does not seems to work with this file, it download a huge
# archive every single build)

# TODO: Multi stage build, when buildout will be brutaly slaughtered \o/

# Note, we use spark 1.6.1 as it is the version that was present on the
# codebase, but there is avaliable release for all the other versions.
# (Including those >= 2.X)

ADD https://archive.apache.org/dist/spark/spark-1.6.1/spark-1.6.1-bin-hadoop2.6.tgz /

RUN tar xvf /spark-1.6.1-bin-hadoop2.6.tgz && \
  mv /spark-1.6.1-bin-hadoop2.6 /opt/spark-1.6.1/
ENV SPARK_HOME /spark-1.6.1-bin-hadoop2.6

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

RUN pip3 install \
  pyspark

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
  chown -R ikats /ikats_py_deploy && \
  chown -R ikats /build && \
  chown -R ikats /logs

USER ikats
EXPOSE 8000

ADD . /ikats_py_deploy

WORKDIR /ikats_py_deploy/docker

ENTRYPOINT ["bash", "container_init.sh"]
