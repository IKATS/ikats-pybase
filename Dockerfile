#FROM hub.ops.ikats.org/ikats-spark
# TODO realign with registry
FROM ikats-spark


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
ADD start_gunicorn.sh ${IKATS_PATH}

RUN chown -R ikats:ikats ${IKATS_PATH}

USER ikats
EXPOSE 8000
WORKDIR ${IKATS_PATH}
ENTRYPOINT ["bash", "container_init.sh"]
