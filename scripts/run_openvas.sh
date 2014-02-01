#!/usr/bin/env bash
#
<<<<<<< HEAD
# Date:    2013-12-30
=======
# Date: 2013-12-30
>>>>>>> master
#
# owtf is an OWASP+PTES-focused try to unite great tools and facilitate pen testing
# Copyright (c) 2011, Abraham Aranguren <name.surname@gmail.com> Twitter: @7a_ http://7-a.org
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
<<<<<<< HEAD
# * Redistributions of source code must retain the above copyright 
=======
# * Redistributions of source code must retain the above copyright
>>>>>>> master
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright owner nor the
# names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
<<<<<<< HEAD
# 
=======
#
>>>>>>> master
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
<<<<<<< HEAD




if [ $# -ne 3 -a $# -ne 4 ]; then
	echo "Usage $0 <tool_dir> <target url> <proxy> (<user agent -spaces replaced by # symbol->)"
=======
#


if [ $# -ne 3 -a $# -ne 4 ]; then
        echo "Usage $0 <tool_dir> <target url> <proxy> (<user agent -spaces replaced by # symbol->)"
>>>>>>> master
        exit
fi


URL1=$1
URL=$(echo $URL1 |sed -e 's/^http:\/\///g' -e 's/^https:\/\///g')
PROXY=$2
USER_AGENT="Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0" # Default to something less obvious
if [ $2 ]; then
<<<<<<< HEAD
	USER_AGENT=$(echo $3 | sed 's/#/ /g') # Expand to real User Agent
fi



DATE=$(date +%F_%R_%S | sed 's/:/_/g')
echo "DATE=$DATE"
OUTFILE="OpenVAS_Main_Report_$DATE"
DIR=$(pwd) # Remember current dir
echo
PORT=$(netstat -evantupo|grep openvas|grep LISTEN| sed 's/  */#/g'|cut -f4 -d# | cut -f2 -d:)

#Port-check doesn't always work as openvassd is sometimes the single process running (without openvasmd and openvasad)
#same thing happens for gsad, so it is better to check for each one

if [ "$PORT" = "" ]; then
   #GSAD=$(netstat -evantupo|grep gsad|grep LISTEN| sed 's/  */#/g' | cut -f9 -d'#' | cut -f1 -d'/')
   #if [ "$GSAD" != "" ];then 
   #   kill -9 $GSAD
   #fi
   
   
   pkill -9 gsad
   sleep 1
   echo "Starting OpenVas Services"
   #this will take time
   openvas-nvt-sync  #this prints output in weird format,same issue as above (progress status)
=======
        USER_AGENT=$(echo $3 | sed 's/#/ /g') # Expand to real User Agent
fi

echo $URL

DATE=$(date +%F_%R_%S | sed 's/:/_/g')
echo "DATE=$DATE"
OUTFILE="openvas_report$DATE"
DIR=$(pwd) # Remember current dir
echo
PORT=$(netstat -evantupo|grep openvas|grep LISTEN| sed 's/ */#/g'|cut -f4 -d# | cut -f2 -d:)

if [ "$PORT" = "" ]; then
   #GSAD=$(netstat -evantupo|grep gsad|grep LISTEN| sed 's/ */#/g' | cut -f9 -d'#' | cut -f1 -d'/')
   #if [ "$GSAD" != "" ];then
   # kill -9 $GSAD
   #fi
   pkill -9 openvas
   pkill -9 gsad
   
   echo "Starting OpenVas Services"
   openvas-nvt-sync
>>>>>>> master
   openvas-scapdata-sync
   openvas-certdata-sync
   openvasmd --rebuild
   openvasmd --backup
   openvassd
   openvasmd
   openvasad
   gsad --http-only --listen=127.0.0.1 -p 9392
   
   sleep 10
<<<<<<< HEAD

else 
     if [ "$(netstat -evantupo|grep openvassd|grep LISTEN| sed 's/  */#/g'|cut -f4 -d# | cut -f2 -d:)" = ""  ]; then 
        
        openvassd
     fi
     if [ "$(netstat -evantupo|grep openvasmd|grep LISTEN| sed 's/  */#/g'|cut -f4 -d# | cut -f2 -d:)" = ""  ]; then
       
        openvasmd
     fi
     if [ "$(netstat -evantupo|grep openvasmd|grep LISTEN| sed 's/  */#/g'|cut -f4 -d# | cut -f2 -d:)" = "" ]; then
        openvasad
     fi
     if [ "$(netstat -evantupo|grep gsad|grep LISTEN| sed 's/  */#/g'|cut -f4 -d# | cut -f2 -d:)" = "" ];then
        
        gsad --http-only --listen=127.0.0.1 -p 9392
        sleep 1
     fi

=======
>>>>>>> master
fi

echo "Runnig OpenVAS Plugin.."
flag=1;
while [ $flag == 1 ]
<<<<<<< HEAD
do 
  read -s -p "Enter password for admin (which you entered during the setup) : `echo  $'\n '`Password :" PASS
  echo  ""
  TARGET_ID=$(omp -u admin -w $PASS -iX '<create_target><name>'OWTF_Target_$URL'</name><hosts>'$URL'</hosts></create_target>'  | sed 's/  *//g'|cut -f2 -d'"')
  if [[ $TARGET_ID = *Targetexistsalready* ]]; then
    echo -e "Target already exists\nExiting from OpenVAS.."
    exit
  fi
  if [ "$TARGET_ID" == "" ]
  then
    echo "Authentication Failure"
  else
    flag=0
  fi   
#echo $TARGET_ID
done
echo "#########################################################################"
echo "###                                                                   ### 
###                      __  __  __            __  __                 ###
###                     |  ||__||__ |\ | \  / |__||__                 ###
###                     |__||   |__ | \|  \/  |  | __|                ###
###                                                                   ###
### "

echo "###--------------Target Created : OWTF_Target_$URL..."
#Default Fast and full Scan
CONFIG_ID="daba56c8-73ec-11df-a475-002264764cea" #by-default Fast and full scan

TASK_ID=$(omp -u admin -w $PASS --xml="<create_task><name>OWTF_Task_$URL</name>
                                       <config id=\"$CONFIG_ID\"/>
                                       <target id=\"$TARGET_ID\"/>
                    </create_task>" |  sed 's/  *//g'|cut -f2 -d'"')
echo "###-------------------------------------------------------------------###"
echo "###--------------Task Created : OWTF_Task_$URL..."

REPORT_ID=$(omp -u admin -w $PASS --xml="<start_task task_id=\"$TASK_ID\"/>" | sed 's/  *//g'|cut -f3 -d'>' |cut -f1 -d'<')
echo "###-------------------------------------------------------------------###"
echo "###--------------Task Started-----------------------------------------###"

echo "###-------------------------------------------------------------------###"

echo "###--------------Status Check-----------------------------------------###"
=======
do
read -s -p "Enter password for admin (which you entered during the setup) : `echo $'\n '`Password :" PASS
  echo ""
  TARGET_ID=$(omp -u admin -w $PASS -iX '<create_target><name>'OWTF_Target_$URL'</name><hosts>'$URL'</hosts></create_target>' | sed 's/ *//g'|cut -f2 -d'"')
  if [[ $TARGET_ID = *Targetexistsalready* ]]; then
echo -e "Target already exists\nExiting from OpenVAS.."
    exit
fi
if [ "$TARGET_ID" == "" ]
  then
echo "Authentication Failure"
  else
flag=0
  fi
#echo $TARGET_ID
done
echo "#####################################################################"

echo "### ###
### __ __ __ __ __ ###
### | ||__||__ |\ | \ / |__||__ ###
### |__|| |__ | \| \/ | | __| ###
### ###
### "

echo "###--------------Target Created : OWTF_Target_$URL..."

CONFIG_ID="daba56c8-73ec-11df-a475-002264764cea" #by-default Fast and full scan

TASK_ID=$(omp -u admin -w $PASS --xml="<create_task><name>OWTF_Task_$URL</name>
<config id=\"$CONFIG_ID\"/>
<target id=\"$TARGET_ID\"/>
</create_task>" | sed 's/ *//g'|cut -f2 -d'"')
echo "###---------------------------------------------------------------###"
echo "###--------------Task Created : OWTF_Task_$URL..."

REPORT_ID=$(omp -u admin -w $PASS --xml="<start_task task_id=\"$TASK_ID\"/>" | sed 's/ *//g'|cut -f3 -d'>' |cut -f1 -d'<')
echo "###---------------------------------------------------------------###"
echo "###--------------Task Started-------------------------------------###"

echo "###---------------------------------------------------------------###"

echo "###--------------Status Check-------------------------------------###"
>>>>>>> master
echo -e "\n"





<<<<<<< HEAD
STATUS=$(omp -u admin -w $PASS -G | grep $TASK_ID|sed 's/  */#/g'|cut -f2,3 -d'#')
#STATUS="NO"
echo "In Progress...Hang tight !!"
echo "(You can check your status of progress by going to http://127.0.0.1:9392 and logging in
with the username 'admin' and the password which you just entered and then going to tasks tab in scan management)".
while [[ $STATUS != *Done* ]]
do
   #All the below statements were for progress bar.But as that is not yet possible in OWTF,
   #I have kept it for future use.
  
   #tput el1
   #tput rc
   #echo -n "###"
   #echo  "$STATUS"| sed -e "s/#/ /g" |sed -e 's/Task.[0-9]*//g'
   #echo -ne "$STATUS\033[0K\r" | sed -e "s/#/ /g" |sed -e 's/Task.[0-9]*//g'
   #echo  "---------------$STATUS...." | sed -e "s/#/ /g" |sed -e 's/Task.[0-9]*//g'
   
   sleep 1 
   
   STATUS=$(omp -u admin -w $PASS -G | grep $TASK_ID |sed 's/  */#/g'|cut -f2,3 -d'#')
   if [[ $STATUS = *Stopped* ]];then
     break
   fi
done

omp -u admin -w $PASS --delete-task $TASK_ID
echo -e "\n"
echo -n "###------------------Done !-------------------------------------------###"
echo -e "\n"
echo "###-------------------------------------------------------------------###"
echo "###--------------Status Check Complete--------------------------------###"
echo "###-------------------------------------------------------------------###"

DIR=$(pwd)
echo "###--------------Creating report in $DIR"...
omp -u admin -w napster --get-report $REPORT_ID  --format 6c248850-1f62-11e1-b082-406186ea4fc5  > $OUTFILE.html
echo "###-------------------------------------------------------------------###"
echo "###--------------Report Generated-------------------------------------###"
echo -e "\n"

echo "###----------------- [*] Done!] --------------------------------------###"
echo "#########################################################################"
=======
STATUS=$(omp -u admin -w $PASS -G | grep $TASK_ID|sed 's/ */#/g'|cut -f2,3 -d'#')
#STATUS="NO"
echo "In Progress..."
while [[ $STATUS != *Done* ]]
do
   
   #echo -ne "One Moment please $sek ... \r"
   #tput el1
   #tput rc
   #echo -n "###"
   #echo "$STATUS"| sed -e "s/#/ /g" |sed -e 's/Task.[0-9]*//g'
   #echo -ne "$STATUS\033[0K\r" | sed -e "s/#/ /g" |sed -e 's/Task.[0-9]*//g'
   #echo "---------------$STATUS...." | sed -e "s/#/ /g" |sed -e 's/Task.[0-9]*//g'
   
   sleep 1
   
   STATUS=$(omp -u admin -w $PASS -G | grep $TASK_ID |sed 's/ */#/g'|cut -f2,3 -d'#')
   if [[ $STATUS = *Stopped* ]];then
break
fi
   #STATUS="Done"
  
done
omp -u admin -w $PASS --delete-task $TASK_ID

echo -n "###------------------Done !---------------------------------------###"
echo -e "\n"

























echo "###---------------------------------------------------------------###"
echo "###--------------Status Check Complete----------------------------###"
echo "###---------------------------------------------------------------###"

DIR=$(pwd)
echo "###--------------Creating report in $DIR"...
omp -u admin -w napster --get-report $REPORT_ID --format 6c248850-1f62-11e1-b082-406186ea4fc5 > $OUTFILE.html
echo "###---------------------------------------------------------------###"
echo "###--------------Report Generated---------------------------------###"
echo -e "\n"

echo
echo "[*] Done!]"
>>>>>>> master
