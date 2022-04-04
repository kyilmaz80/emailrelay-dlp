FROM python:3-slim
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

#ENV INSTALL_PATH /scripts

WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get -y --no-install-recommends install poppler-utils \
  && apt-get -y install wget git \
  && rm -rf /var/lib/apt/lists/*

RUN rm -rf emailrelay-dlp

RUN git clone --depth 1 https://github.com/kyilmaz80/emailrelay-dlp

#RUN mkdir emailrelay-dlp

#COPY * emailrelay-dlp/

WORKDIR /usr/src/app/emailrelay-dlp/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1235

CMD [ "python", "./parse_server.py" ]

