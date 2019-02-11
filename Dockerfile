FROM ikats/spark:develop

LABEL license="Apache License, Version 2.0"
LABEL copyright="CS Systèmes d'Information"
LABEL maintainer="contact@ikats.org"
LABEL version="0.9.1"

COPY assets/requirements.txt /tmp
WORKDIR /tmp

ENV IKATS_PATH /ikats
ENV TSDATA /ikats/TSdata

RUN pip3 install -r requirements.txt \
  && rm requirements.txt \
  && groupadd \
    -r ikats && \
  useradd \
    -r \
    -g ikats \
    -s /sbin/nologin \
    -c "Docker image user" \
    ikats \
  && mkdir -p ${IKATS_PATH} /logs && \
  chown -R ikats:ikats /logs

COPY src/ ${IKATS_PATH}
COPY assets/gunicorn.py.ini ${IKATS_PATH}
COPY assets/container_init.sh ${IKATS_PATH}
COPY assets/start_gunicorn.sh ${IKATS_PATH}
COPY assets/ikats.env ${IKATS_PATH}

RUN chown -R ikats:ikats ${IKATS_PATH} /opt/spark /start_spark.sh

WORKDIR ${IKATS_PATH}
USER ikats
RUN mkdir -p ${TSDATA}

VOLUME ${IKATS_PATH}
EXPOSE 8000
ENTRYPOINT ["bash", "container_init.sh"]
