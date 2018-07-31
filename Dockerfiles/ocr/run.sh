#!/bin/bash

[ "${DEBUG}" == "yes" ] && set -x

#Start services
supervisord -c /etc/supervisord.conf
