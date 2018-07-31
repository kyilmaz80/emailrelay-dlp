FROM python:3.5
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

ENV INSTALL_PATH /scripts

WORKDIR $INSTALL_PATH

RUN apt-get update && \
	apt-get -y --install-suggests install poppler-utils && \
    apt-get -y install wget && \
    apt-get -y install supervisor && \
    apt-get -y install git

COPY run.sh $INSTALL_PATH/
COPY etc/supervisord.conf /etc/supervisord.conf
COPY etc/supervisord.d/*.ini /etc/supervisord.d/
RUN chmod +x $INSTALL_PATH/run.sh

RUN rm -rf emailrelay-dlp

RUN rm -rf postfix-filter-loop

RUN git clone --depth 1 -b postfix-python-filter --single-branch https://github.com/kyilmaz80/emailrelay-dlp.git

WORKDIR $INSTALL_PATH/emailrelay-dlp/

ADD params.py $INSTALL_PATH/emailrelay-dlp/params.py

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR $INSTALL_PATH/

RUN git clone --depth 1 https://github.com/kyilmaz80/postfix-filter-loop

WORKDIR $INSTALL_PATH/postfix-filter-loop/

EXPOSE 10025

CMD ["/scripts/run.sh"]





