
#!/bin/bash
if [[ -z $1 ]] || [[ -z $2 ]]; then
 echo "SMTP Sunucu IP ve Port girilmedi!"
 exit
fi


if [[ $1 == "mydlp" ]]; then
  echo " TG 3 MyDLP Send Attachments baslatiliyor..."
  #ilk once gönderme öncesi toplam log sayisi bulunur ve mydlp_log_csv dosyasına yazilir
  jmeter -n -t TestPlan-Cont.jmx -p props/TestPlan_TG6.properties
  mydlp_log_kaydi=`cat mydlp_log_cnt.csv`
  echo "MyDLP'de msj gönderim öncesi $mydlp_log_kaydi kadar kayit logu var..."
else
  echo "TG 3 EMailRelay Send Attachment DLP baslatiliyor..."
  #rm "mydlp_log_cnt.csv"
fi


jmeter -n -t TestPlan-Cont.jmx -p props/TestPlan_TG3.properties -Jsmtp.server=$1 -Jsmtp.port=$2
