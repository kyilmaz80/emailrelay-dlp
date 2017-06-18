#!/bin/bash

#mydlp'de dlp mesajların log'lanmadan önceki toplam log sayısını bulur.

re='^[0-9]+$'
if [ -f mydlp_log_cnt.csv ]; then
 mydlp_log_gonder_oncesi=`cat mydlp_log_cnt.csv`
 if [[ $mydlp_log_gonder_oncesi =~ $re ]]; then
  jmeter -n -t TestPlan-Cont.jmx -p props/TestPlan_TG6.properties
  mydlp_log_gonder_sonrasi=`cat mydlp_log_cnt.csv`
  mydlp_leaked=`expr $mydlp_log_gonder_sonrasi - $mydlp_log_gonder_oncesi`
  echo "MyDLP leak saptanan değer: $mydlp_leaked"
 fi
fi
echo "TG 7 Mail Recieve Test baslatiliyor..."
if [ -f msgs.csv ]; then
    COUNT=`cat msgs.csv|wc -l`
    echo "msgs.csv dosyasinda $COUNT adet mesaj postfix sunucudan okunacak..."
fi

if [ -z $1 ]; then
  read -p "Devam [ENTER]"
fi
#mydlp testi yapılıyorsa messages.leaked den gönder değeri
if [[ -f mydlp_log_cnt.csv ]] && [[ $mydlp_log_gonder_oncesi =~ $re ]]  ; then
 echo "MyDLP sunucu icin mail recieve..."
 jmeter -n -t TestPlan-Cont.jmx -p props/TestPlan_TG7.properties -Jmessages.total=$COUNT -Jmessages.leaked=$mydlp_leaked
else
 jmeter -n -t TestPlan-Cont.jmx -p props/TestPlan_TG7.properties -Jmessages.total=$COUNT
fi
 
lastCSV=`ls -lahtr | grep csv |grep Send | tail -1 | awk '{print $9}'`
cnt=`cat $lastCSV|wc -l`
echo "--------------------------------------------"
echo "$lastCSV dosyasinda $cnt veri elde edildi..."
echo "--------------------------------------------"

isassert=`cat mailreader_assertions.jtl |wc -l`

if [[ $isassert != "1" ]]; then
  echo "---------Assertions jtl-------------------"
  cat mailreader_assertions.jtl 
  echo "------------------------------------------"
fi

if [ -z $1 ]; then
  read -p "msgs.csv, mydlp_log_cnt.csv ve mail ler temizlenecek. [ENTER] ?"
fi
./clearResults_testbaslat.sh

