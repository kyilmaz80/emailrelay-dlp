#!/bin/bash
if [[ -z $1 ]] || [[ -z $2 ]]; then
 echo "Kullanim: ./recieveMsg_testbaslat.sh [toplam_atilan_mesaj] [dlp_mesaj]"
 exit
fi
echo "TG 3 Mail Recieve Test baslatiliyor..."
jmeter -n -t TestPlan.jmx -p props/TestPlan_TG3.properties -Jmessages.total=$1 -Jmessages.leaked=$2
read -p "msgs.csv ve mail ler temizlenecek. [ENTER] ?"
./clearResults_testbaslat.sh
