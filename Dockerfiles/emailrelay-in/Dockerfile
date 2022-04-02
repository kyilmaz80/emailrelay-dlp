FROM dcagatay/emailrelay
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

COPY mail.pem /etc/ssl/certs/
CMD ["--log", "--port","587","--poll", "5", "--remote-clients", "--client-tls", "--tls-config=1", "--server-tls", "/etc/ssl/certs/mail.pem","--forward", "--forward-to", "emailrelay-out:10025" ]

