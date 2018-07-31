#!/bin/bash

[ "${DEBUG}" == "yes" ] && set -x

function add_config_value() {
  local key=${1}
  local value=${2}
  local config_file=${3:-/etc/postfix/main.cf}
  [ "${key}" == "" ] && echo "ERROR: No key set !!" && exit 1
  [ "${value}" == "" ] && echo "ERROR: No value set !!" && exit 1

  echo "Setting configuration option ${key} with value: ${value}"
  sed -i -e "/^#\?\(\s*${key}\s*=\s*\).*/{s//\1${value}/;:a;n;:ba;q}" \
         -e "\$a${key}=${value}" \
         ${config_file}
}

function add_master_config() {
   local config_file=${3:-/etc/postfix/master.cf}
   local f1=`grep -oE "^scan unix - - n - 10 smtp -o smtp_send_xforward_command=yes$" ${config_file}`
   local f2=`grep -oE "^         \-o disable_mime_output_conversion=yes$" ${config_file}`
   local f3=`grep -oE "^\[[a-z.]*\]:[0-9]* inet n - n - 10 smtpd$" ${config_file}`
   local f4=`grep -oE "^         \-o content_filter=$" ${config_file}`
   local f5=`grep -oE "^         \-o receive_override_options=no_unknown_recipient_checks,no_header_body_checks,no_milters$" ${config_file}`
   local f6=`grep -oE "^         \-o smtpd_authorized_xforward_hosts=[0-9,./]*" ${config_file}`

   if [ -z ${f1} ] && [ -z ${f2} ] && [ -z ${f3} ] && [ -z ${f4} ] && [ -z ${f5} ] && [ -z ${f6} ]; then
     echo "scan unix - - n - 10 smtp -o smtp_send_xforward_command=yes" >> ${config_file}
     echo "         -o disable_mime_output_conversion=yes" >> ${config_file}
     echo "" >> ${config_file}
     echo "[${POSTFIX_DLP_IP}]:${POSTFIX_DLP_PORT} inet n - n - 10 smtpd" >> ${config_file}
     echo "         -o content_filter=" >> ${config_file}
     echo "         -o receive_override_options=no_unknown_recipient_checks,no_header_body_checks,no_milters" >> ${config_file}
     echo "         -o smtpd_authorized_xforward_hosts=127.0.0.0/8,${FILTER_SERVER_IP},${SMTP_SERVER_IP}" >> ${config_file}
   fi
}

[ -z "${FILTER_SERVER}" ] && echo "FILTER_SERVER is not set" && exit 1
[ -z "${POSTFIX_DLP_SERVER}" ] && echo "POSTFIX_DLP_SERVER is not set" && exit 1

FILTER_SERVER_IP=`ping ${FILTER_SERVER} -c 1 | grep from|grep -oE '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}'`
POSTFIX_DLP_IP=`ping ${POSTFIX_DLP_SERVER} -c 1 | grep from|grep -oE '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}'`
export FILTER_SERVER_IP=$FILTER_SERVER_IP
export POSTFIX_DLP_IP=$POSTFIX_DLP_IP

[ -z "${SMTP_SERVER}" ] && echo "SMTP_SERVER is not set" && exit 1
[ -z "${SMTP_USERNAME}" ] && echo "SMTP_USERNAME is not set" && exit 1
[ -z "${SMTP_PASSWORD}" ] && echo "SMTP_PASSWORD is not set" && exit 1
[ -z "${POSTFIX_DLP_HOSTNAME}" ] && echo "POSTFIX_DLP_HOSTNAME is not set" && exit 1
[ -z "${SMTP_SERVER_IP}" ] && echo "SMTP_SERVER_IP is not set" && exit 1
[ -z "${FILTER_SERVER_IP}" ] && echo "FILTER_SERVER_IP is not set" && exit 1
[ -z "${POSTFIX_DLP_IP}" ] && echo "POSTFIX_DLP_IP is not set" && exit 1
#[ -z "${POSTFIX_FILTER_SERVER}" ] && echo "POSTFIX FILTER SERVER is not set" && exit 1
#[ -z "${POSTFIX_FILTER_SERVER_PORT}" ] && echo "POSTFIX FILTER SERVER PORT is not set" && exit 1


SMTP_PORT="${SMTP_PORT-587}"

#Get the domain from the server host name
DOMAIN=`echo ${POSTFIX_DLP_HOSTNAME} |awk -F. '{$1="";OFS="." ; print $0}' | sed 's/^.//' | sed 's/ /./g'`

# Set needed config options
add_config_value "myhostname" ${POSTFIX_DLP_HOSTNAME}
add_config_value "mydomain" ${DOMAIN}
add_config_value "mydestination" '$myhostname, localhost.$mydomain,localhost, $mydomain'
add_config_value "myorigin" '$mydomain'
add_config_value "relayhost" "[${SMTP_SERVER_IP}]:${SMTP_PORT}"
add_config_value "smtp_use_tls" "yes"
add_config_value "smtp_sasl_auth_enable" "yes"
add_config_value "smtp_sasl_password_maps" "hash:\/etc\/postfix\/sasl_passwd"
add_config_value "smtp_sasl_security_options" "noanonymous"
add_config_value "content_filter" "scan:[${FILTER_SERVER_IP}]:${FILTER_SERVER_PORT}"
add_config_value "receive_override_options" "no_address_mappings"

# change master conf
add_master_config

# Create sasl_passwd file with auth credentials
if [ ! -f /etc/postfix/sasl_passwd ]; then
  grep -q "${SMTP_SERVER}" /etc/postfix/sasl_passwd  > /dev/null 2>&1
  if [ $? -gt 0 ]; then
    echo "Adding SASL authentication configuration"
    echo "[${SMTP_SERVER}]:${SMTP_PORT} ${SMTP_USERNAME}:${SMTP_PASSWORD}" >> /etc/postfix/sasl_passwd
    postmap /etc/postfix/sasl_passwd
  fi
fi

#Start services
supervisord
