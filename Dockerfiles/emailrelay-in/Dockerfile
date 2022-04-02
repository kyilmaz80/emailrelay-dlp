FROM dcagatay/emailrelay
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

COPY mail.pem /etc/ssl/certs/
CMD [ "--poll","5", "--forward", "--forward-to", "emailrelay-out:10025",  "--server-tls-certificate=/etc/ssl/certs/mail.pem", "--server-tls", "--client-tls", "--tls-config=1"] 

