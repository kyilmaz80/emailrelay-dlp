FROM openjdk:11
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

ENV INSTALL_PATH /opt

WORKDIR $INSTALL_PATH
ADD config.xml ./
ENV TIKA_JAR="tika-server.jar" \
    TIKA_MEMORY="1g" \
    TIKA_VERSION="2.3.0"

LABEL description="Apache Tika Server" \
      version=${TIKA_VERSION}


RUN apt-get install -y --no-install-recommends wget \
        && rm -rf /var/lib/apt/lists/*

RUN wget https://downloads.apache.org/tika/${TIKA_VERSION}/tika-server-standard-${TIKA_VERSION}.jar -O $INSTALL_PATH/${TIKA_JAR}

COPY . .
EXPOSE 9998

ENTRYPOINT java -Xmx${TIKA_MEMORY} -jar /opt/${TIKA_JAR} -h 0.0.0.0
CMD ["--log", "--debug"]


