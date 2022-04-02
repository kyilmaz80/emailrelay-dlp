#!/bin/bash

COMMON_NAME=$1
NUM_DAYS=365

if [ -z $COMMON_NAME ]; then
  COMMON_NAME=`hostname -f`
fi

echo "$COMMON_NAME certificate generating..."

DOMAIN_NAME=`echo $COMMON_NAME | cut -d '.' -f2-100`

SUBJ=""/C=TR/ST=ANKARA/L=ANKARA/O=KORGICORP/OU=IT/CN=$COMMON_NAME/emailAddress=root@$DOMAIN_NAME""

#ca
openssl req -nodes -x509 -newkey rsa:2048 -keyout /tmp/ca.key -out /tmp/ca.crt -subj $SUBJ

#server
openssl req -nodes -newkey rsa:2048 -keyout /tmp/server.key -out /tmp/server.csr -subj $SUBJ -days $NUM_DAYS

openssl x509 -req -in /tmp/server.csr -CA /tmp/ca.crt -CAkey /tmp/ca.key -CAcreateserial -out /tmp/server.crt -days $NUM_DAYS

cat /tmp/server.key /tmp/server.crt > mail.pem

#client
openssl req -nodes -newkey rsa:2048 -keyout /tmp/client.key -out /tmp/client.csr -subj $SUBJ -days $NUM_DAYS

openssl x509 -req -in /tmp/client.csr -CA /tmp/ca.crt -CAkey /tmp/ca.key -CAserial /tmp/ca.srl -out /tmp/client.crt -days $NUM_DAYS

cat /tmp/client.key /tmp/client.crt > client.pem


