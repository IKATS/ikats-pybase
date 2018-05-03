FROM ikats/spark

ADD assets/requirements.txt /tmp
WORKDIR /tmp
RUN pip3 install -r requirements.txt \
  && rm requirements.txt

RUN \
  groupadd \
    -r ikats && \
  useradd \
    -r \
    -g ikats \
    -s /sbin/nologin \
    -c "Docker image user" \
    ikats

ENV IKATS_PATH /ikats
ENV PYSPARK_PYTHON python3

RUN \
  mkdir ${IKATS_PATH} && \
  mkdir /logs && \
  chown -R ikats:ikats /logs

ADD src/ ${IKATS_PATH}

ADD assets/gunicorn.py.ini ${IKATS_PATH}
ADD assets/container_init.sh ${IKATS_PATH}
ADD assets/start_gunicorn.sh ${IKATS_PATH}
ADD assets/ikats.env ${IKATS_PATH}

RUN chown -R ikats:ikats ${IKATS_PATH} /opt/spark /start_spark.sh

WORKDIR ${IKATS_PATH}
USER ikats

EXPOSE 8000
ENTRYPOINT ["bash", "container_init.sh"]
