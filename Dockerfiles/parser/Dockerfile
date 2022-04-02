FROM python:3.10.4-bullseye
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

ENV INSTALL_PATH /scripts

WORKDIR $INSTALL_PATH

RUN apt-get update && \
	apt-get -y --install-suggests install poppler-utils && \
    apt-get -y install wget && \
    apt-get -y install git

RUN rm -rf emailrelay-dlp

RUN git clone --depth 1 https://github.com/kyilmaz80/emailrelay-dlp

WORKDIR $INSTALL_PATH/emailrelay-dlp/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1235

CMD [ "python", "./parse_server.py" ]

