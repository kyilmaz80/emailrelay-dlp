FROM alpine:latest

RUN apk update && apk add tzdata \
     && cp -r -f /usr/share/zoneinfo/Europe/Istanbul /etc/localtime

ADD crontab.txt /crontab.txt
ADD script.sh /script.sh
ADD emailrelay-resubmit /emailrelay-resubmit
COPY entry.sh /entry.sh
RUN chmod 755 /script.sh /entry.sh
RUN /usr/bin/crontab /crontab.txt

CMD ["/entry.sh"]
