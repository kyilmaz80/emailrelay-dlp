#!/bin/bash
#KORAYY
#170412
#OTOMATIK E-POSTA DLP TEST BETIGI
#Rev 5

SERVER=$1
PORT=$2
TESTNO=$3
TOTALDATA=120
TIME=`date +"%Y%m%d%H%M"`

get_count_for_test() {
  local test_no=$1
  local users=$(get_total_users_for_test $test_no)
  local count=$((TOTALDATA/users))
  echo ${count}
}

get_total_users_for_test() {
  test_no=$1
  users=$(cat "props/TestPlan_TG$test_no.properties" |grep "threadGroup$test_no.users"|cut -d "=" -f2)
  duration=$(cat "props/TestPlan_TG$test_no.properties" |grep "threadGroup$test_no.duration"|cut -d "=" -f2)
  local total_users=$((users*duration))
  echo ${total_users}
}

get_duration_for_test() {
  test_no=$1
  duration=$(cat "props/TestPlan_TG$test_no.properties" |grep "threadGroup$test_no.duration"|cut -d "=" -f2)
  echo $duration
}

change_user_count_for_test() {
  # T10, T20, T30, T40
  test_no=$1
  local total_users=$(get_total_users_for_test $test_no)
  local duration=$(get_duration_for_test $test_no)
  local users=$((total_users/duration))
 
  if [[ $total_users == 10 ]]; then
    echo "change_user_count_for_test(): T10 -> T20 degistiriliyor..."
    sed -i "s/threadGroup$test_no.users=${users}/threadGroup$test_no.users=4/g" "props/TestPlan_TG$test_no.properties"
    # users -> 4 yap
  elif [[ $total_users == 20 ]]; then
    echo "change_user_count_for_test(): T20 -> T30 degistiriliyor..."
    sed -i "s/threadGroup$test_no.users=${users}/threadGroup$test_no.users=6/g" "props/TestPlan_TG$test_no.properties"
    # users-> 6 yap
  elif [[ $total_users == 30 ]]; then
    echo "change_user_count_for_test(): T30 -> T40 degistiriliyor..."
    sed -i "s/threadGroup$test_no.users=${users}/threadGroup$test_no.users=8/g" "props/TestPlan_TG$test_no.properties"
    # users -> 8 yap
  else
    echo "change_user_count_for_test(): T40 -> T10 degistiriliyor..."
    sed -i "s/threadGroup$test_no.users=${users}/threadGroup$test_no.users=2/g" "props/TestPlan_TG$test_no.properties"
    # 2 yap
  fi
}

test_dir_create() {
  local TIME=`date +"%Y%m%d%H%M"`
  local test_no=$1
  local total_users=$(get_total_users_for_test $test_no)
  local test_type=$2
  #local TEST_TYPE1="data_no_filter"
  #local TEST_TYPE2="data_local_parse"
  #local TEST_TYPE3="data_remote_parse"
  #local TEST_TYPE4="data_mydlp"

  # hangi test türü ise secilir.
  local dir_name="$SERVER/$test_type/test$test_no/T$total_users/$TIME"
  
  if [ ! -d $dir_name  ]; then
    mkdir -p $dir_name
  fi
  echo $dir_name
}


test_run() {
     testno=$1
     test_type=$2
     local TEST_DIR=$(test_dir_create $testno $test_type)

      # Test 1: Send Text, Test 2: Send DLP Text, Test 3: Send Attachment, Test 4: Send Attachment OCR
      if [[ $testno == 1 ]]; then
	  echo "Test $testno Send Text"
        ./sendTextMsg_testbaslat.sh $SERVER $PORT >> "${TEST_DIR}/log_${SERVER}_send_test${testno}.log"
      elif [[ $testno == 2 ]]; then
	  echo "Test $testno Send DLP Text"
         ./sendTextDLPMsg_testbaslat.sh $SERVER $PORT >> "${TEST_DIR}/log_${SERVER}_send_test${testno}.log"
      elif [[ $testno == 3 ]]; then
	  echo "Test $testno Send Attachment"
         ./sendAttachMsg_testbaslat.sh $SERVER $PORT >> "${TEST_DIR}/log_${SERVER}_send_test${testno}.log"
      elif [[ $testno == 4 ]]; then
	  echo "Test $testno Send OCR Attachment"
          ./sendAttachOCRMsg_testbaslat.sh $SERVER $PORT >> "${TEST_DIR}/log_${SERVER}_send_test${testno}.log"
      else
         echo "pass"
      fi
      cat "${TEST_DIR}/log_${SERVER}_send_test${testno}.log"
      #counter=$(( $counter + 1 ))
      #echo 1 dakika bekleniyor
      #sleep 1
      echo Recieving messages
      ./recieveMsg_testbaslat.sh -y  >> "${TEST_DIR}/log_${SERVER}_recv_test${testno}.log"
      cat "${TEST_DIR}/log_${SERVER}_recv_test${testno}.log"
 #   done

    echo "Dosyalar tasiniyor..."
    mv jmeter.log ${TEST_DIR}/
    mv mailreader_assertions.jtl ${TEST_DIR}/
    mv results.jtl ${TEST_DIR}/
    mv response.jtl ${TEST_DIR}/
    mv ${SERVER}*.csv  ${TEST_DIR}/

    echo "**********TEST${testno} BITTI**************"
}


if [ -z $1 ] || [ -z $2 ]; then
 echo "DLP Eposta sunucu ve port girilmedi!"
 exit
fi

if [ -z $3 ]; then
 echo "Test No girilmedi! 1,2,3 ya da 4 girilmeli!"
 exit
else
 TESTNO=$3
fi

#local TEST_TYPE1="data_no_filter"
#local TEST_TYPE2="data_local_parse"
#local TEST_TYPE3="data_remote_parse"
#local TEST_TYPE4="data_mydlp"

if [ -z $4 ]; then
 echo "Test tipi girilmedi! data_no_filter,data_local_parse,data_remote_parse,data_mydlp"
 exit
else
 test_type=$4
fi

if [[ $TESTNO == 1 ]]; then
  echo "Test 1 Send Text baslatiliyor..."
  total_users=$(get_total_users_for_test 1)
  echo "Total Users = T$total_users"
  echo "Test 1 ()"
  
  #T10, T20, T30, T40 oldugundan 4 kere donecez
  cnt=1
  while [[ $cnt -le 4 ]]; do
      echo "Counter = $cnt" 
      echo "test1_run"
      test_run 1 $test_type
      echo "10s bekleniyor.."
      sleep 10
      cnt=$(( $cnt + 1 ))
      change_user_count_for_test 1
  done

elif [[ $TESTNO == 2 ]]; then
  echo "Test 2 Send DLP Text baslatiliyor..."
  total_users=$(get_total_users_for_test 2)
  echo "Total Users = T$total_users"
  echo "Test 2 ()"

  #T10, T20, T30, T40 oldugundan 4 kere donecez
  cnt=1
  while [[ $cnt -le 4 ]]; do
      echo "Counter = $cnt" 
      echo "test2_run"
      test_run 2 $test_type
      echo "10 s bekleniyor.."
      sleep 10
      cnt=$(( $cnt + 1 ))
      change_user_count_for_test 2
  done

elif [[ $TESTNO == 3 ]]; then
  echo "Test 3 Send Attachment baslatiliyor..."
  total_users=$(get_total_users_for_test 3)
  echo "Total Users = T$total_users"
  echo "Test 3 ()"

  #T10, T20, T30, T40 oldugundan 4 kere donecez
  cnt=1
  while [[ $cnt -le 4 ]]; do
      echo "Counter = $cnt" 
      echo "test3_run"
      test_run 3 $test_type
      echo "10 s bekleniyor.." 
      sleep 10
      cnt=$(( $cnt + 1 ))
      change_user_count_for_test 3
  done

elif [[ $TESTNO == 4 ]]; then
  echo "Test 4 Send Attachment OCR baslatiliyor..."
  total_users=$(get_total_users_for_test 4)
  echo "Total Users = T$total_users"
  echo "Test 4 ()"

  #T10, T20, T30, T40 oldugundan 4 kere donecez
  cnt=1
  while [[ $cnt -le 4 ]]; do
      echo "Counter = $cnt" 
      echo "test4_run"
      test_run 4 $test_type
      echo "10 s bekleniyor.." 
      sleep 10
      cnt=$(( $cnt + 1 ))
      change_user_count_for_test 4
  done

else 
  echo "Yanlis Test numarasi!"
  exit
fi

