#!/bin/bash

/entrypoint.sh influxd &
sleep 20

THRESHOLD=2

for token in $(influx auth list | grep -E -v -w "admin's Token|ID" | awk '{print $1}'); do echo $token; influx auth delete --id $token; done

TOKEN_COUNT=$(influx auth list | wc -l)
if [ "$TOKEN_COUNT" -eq "$THRESHOLD" ]; then
   influx  org list  | awk '{print $1}' | grep -v ID > org
   influx auth create --org kalogeropoulos_org  --all-access | awk '{print $2}' | grep -v Description > token
   cp org /connection_info
   cp token /connection_info
else
   echo "Token count is $TOKEN_COUNT, No action taken."	
fi 
tail -f /dev/null
