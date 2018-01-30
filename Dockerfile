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
ADD requirements.txt /tmp
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

ENV IKATS_PATH /ikats
ENV SPARK_HOME /opt/spark-1.6.1
ENV PYSPARK_PYTHON python3

RUN \
  mkdir ${IKATS_PATH} && \
  mkdir /logs && \
  chown -R ikats:ikats /logs

ADD _sources/ikats_core/src/ ${IKATS_PATH}
ADD _sources/ikats_algos/src/ ${IKATS_PATH}
ADD _sources/ikats_django/src/ ${IKATS_PATH}

ADD gunicorn.py.ini ${IKATS_PATH}
ADD container_init.sh ${IKATS_PATH}

RUN chown -R ikats:ikats ${IKATS_PATH}

USER ikats
EXPOSE 8000
WORKDIR ${IKATS_PATH}
ENTRYPOINT ["bash", "container_init.sh"]
