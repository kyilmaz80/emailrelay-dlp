#!/bin/bash

[ "${DEBUG}" == "yes" ] && set -x

POSTFIX_SERVER_IP=`ping ${POSTFIX_DLP_SERVER} -c 1 | grep from|grep -oE '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}'`

echo "$POSTFIX_SERVER_IP ${POSTFIX_DLP_HOSTNAME}" >> /etc/hosts

#Start services
supervisord -c /etc/supervisord.conf
