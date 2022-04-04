FROM dcagatay/emailrelay
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

#COPY mail.pem /etc/ssl/certs/
CMD [ "--poll","5", "--forward", "--forward-to", "emailrelay-out:${ER_OUT_PORTNO}", "--client-tls", "--tls-config=tlsv1.2"] 

